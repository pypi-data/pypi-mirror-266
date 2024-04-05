import inspect
import json
import logging
import threading
import time

from ofdcomparer.dto_error_descriptions import get_dto_error_code_description
from ofdcomparer.libfptr10 import IFptr


class DTO10Helper:
    def __init__(self, fptr=None):
        self.fptr = fptr

        # Информация о ФН
        self.fnWarnings = None
        self.fnVersion = None
        self.fnValidityDate = None
        self.fnSerial = None
        self.fnRegistrationsRemaining = None
        self.fnNumberOfRegistrations = None
        self.fnLivePhase = None
        self.fnFfdVersion = None
        self.fnContainsKeysUpdaterServerUri = None
        self.FfdVersion = None
        self.fnExecution = None

        # Информация о регистрации
        self.device = None
        self.autoMode = None
        self.bso = None
        self.defaultTaxationType = None
        self.encryption = None
        self.excise = None
        self.ffdVersion = None
        self.fnsUrl = None
        self.gambling = None
        self.internet = None
        self.lottery = None
        self.machineInstallation = None
        self.machineNumber = None
        self.ofdChannel = None
        self.offlineMode = None
        self.paymentsAddress = None
        self.registrationNumber = None
        self.service = None

        # ofd
        self.ofd = None
        self.dns = None
        self.host = None
        self.name = None
        self.port = None
        self.vatin = None

        # organization
        self.organization = None
        self.address = None
        self.agents = None
        self.email = None
        self.name = None
        self.taxationTypes = None
        self.vatin = None

        if fptr is None:
            while True:
                try:
                    self.fptr = IFptr()
                except Exception:
                    raise Exception("Error creating DTO 10")
                if self.fptr.interface.value is not None:
                    break

        self.dto10_version = self.fptr.version().decode("cp866")

        self.ErrorCode = None
        self.ErrorDescription = None
        self.JsonAnswer = None

        if fptr is None:
            self.fptr.setSingleSetting(
                self.fptr.LIBFPTR_SETTING_MODEL, str(self.fptr.LIBFPTR_MODEL_ATOL_AUTO)
            )
        self.RNM = self.get_rnm_number()
        self.FN = self.get_fn_number()
        self.get_registration_data()
        self.get_fn_data()

    def get_information_and_status(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_DATA_TYPE, self.fptr.LIBFPTR_DT_STATUS
        )
        self.fptr.queryData()
        self.request_error_code()
        serial_number = self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        return serial_number

    def open(self):
        self.fptr.open()
        return self.request_error_code()

    def close(self):
        self.fptr.close()
        return self.request_error_code()

    def request_error_code(self, flag_all_kkt_settings=False):
        self.ErrorCode = self.fptr.errorCode()
        self.ErrorDescription = self.fptr.errorDescription()
        pytest_dto_error_description = get_dto_error_code_description(self.ErrorCode)
        if self.ErrorDescription != pytest_dto_error_description:
            logging.error(f"Код ошибки ДТО: {self.ErrorCode}")
            logging.error(
                f"ДТО [{self.ErrorDescription}] <-> "
                f"[{pytest_dto_error_description}] const.dto_error_descriptions"
            )
            logging.error(
                "НЕОБХОДИМО АКТУАЛИЗИРОВАТЬ СЛОВАРЬ ALL_DTO10_ERROR_DESCRIPTIONS"
            )
        if self.ErrorCode != self.fptr.LIBFPTR_OK:
            if (
                    flag_all_kkt_settings
                    and self.ErrorCode == self.fptr.LIBFPTR_ERROR_NOT_SUPPORTED
            ):
                pass
            else:
                logging.error(
                    "[ДТО]: Код ошибки: {} [{}]".format(
                        self.ErrorCode, self.ErrorDescription
                    )
                )
        return self.ErrorCode

    def get_last_fiscal_document_number(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_FN_DATA_TYPE, self.fptr.LIBFPTR_FNDT_LAST_DOCUMENT
        )
        self.fptr.fnQueryData()
        self.request_error_code()
        return int(self.fptr.getParamInt(self.fptr.LIBFPTR_PARAM_DOCUMENT_NUMBER))

    def get_last_fd_number(self):
        logging.debug("get_last_fd_number()")
        try:
            json_task = {"type": "getFnStatus"}
            fn_status = self.execute_json(json_task)
            logging.debug("СТАТУС ФН: %s", fn_status)
            last_fd_number = fn_status["fnStatus"]["fiscalDocumentNumber"]
            logging.debug(f"get_last_fd_number() > {last_fd_number}")
            logging.info("ФД: %s", last_fd_number)
            return last_fd_number
        except Exception as e:
            logging.error("get_last_fd_number error: {}".format(e))
            logging.debug("get_last_fd_number() > None")
            return None

    def get_fd_from_fn(self, fd: int):
        """
        Извлечение ФД из ФН
        """
        logging.debug(f"get_fd_from_fn() < {fd}")
        if fd is None:
            logging.debug(f"get_fd_from_fn() > None")
            return None
        # JSON задание для чтения документа из ФН

        json_task = {
            "type": "getFnDocument",
            "fiscalDocumentNumber": int(fd),
            "withRawData": False,
        }
        fd_fn = self.execute_json(json_task)
        if fd_fn is None:
            return None
        if isinstance(fd_fn, dict):
            fd_fn = fd_fn["documentTLV"]
            return fd_fn
        return None

    def connect_to_kkt_by_usb(self, usb_device_path="auto"):
        logging.debug("Устанавливаем соединение с ККТ по USB...")
        self.set_connection_settings_to_usb(usb_device_path)
        if self.open() != self.fptr.LIBFPTR_OK:
            logging.error("Не удалось установить соединение с ККТ")
            return False
        if not self.is_connection_type_usb():
            return False
        logging.info("Соединение с ККТ установлено по USB")
        return True

    def connect_to_kkt_by_ethernet(self, ip="127.0.0.1", port="5555"):
        logging.debug(f"Устанавливаем соединение по ip {ip}:{port}")
        self.set_connection_settings_to_ethernet(ip, port)
        err = self.open()
        if err != self.fptr.LIBFPTR_OK:
            logging.info(f"Ошибка - не удалось установить соединение с ККТ ({err})")
            return False
        if not self.is_connection_type_ethernet():
            return False
        logging.info(
            f"Соединение с ККТ установлено по Ethernet. ip=[{ip}] port=[{port}]"
        )
        return True

    def set_connection_settings_to_ethernet(self, ip, port):
        self.fptr.setSingleSetting(
            self.fptr.LIBFPTR_SETTING_PORT, str(self.fptr.LIBFPTR_PORT_TCPIP)
        )
        self.fptr.setSingleSetting(self.fptr.LIBFPTR_SETTING_IPADDRESS, str(ip))
        self.fptr.setSingleSetting(self.fptr.LIBFPTR_SETTING_IPPORT, str(port))
        self.fptr.applySingleSettings()
        return self.request_error_code()

    def is_connection_type_ethernet(self):
        if not self.fptr.isOpened():
            return False
        connection_type = self.fptr.getSingleSetting(self.fptr.LIBFPTR_SETTING_PORT)
        if not int(connection_type) == self.fptr.LIBFPTR_PORT_TCPIP:
            logging.error(
                f"Способ связи с ККТ [{connection_type}], а должен быть [Ethernet]"
            )
            return False
        return True

    def set_connection_settings_to_usb(self, usb_device_path):
        self.fptr.setSingleSetting(
            self.fptr.LIBFPTR_SETTING_PORT, str(self.fptr.LIBFPTR_PORT_USB)
        )
        self.fptr.setSingleSetting(
            self.fptr.LIBFPTR_SETTING_USB_DEVICE_PATH, str(usb_device_path)
        )
        self.fptr.applySingleSettings()
        return self.request_error_code()

    def is_connection_type_usb(self):
        if not self.fptr.isOpened():
            return False
        connection_type = self.fptr.getSingleSetting(self.fptr.LIBFPTR_SETTING_PORT)
        self.request_error_code()
        if not int(connection_type) == self.fptr.LIBFPTR_PORT_USB:
            logging.error(
                "Способ связи с ККТ [{}], а должен быть [USB]".format(connection_type)
            )
            return False
        return True

    def connect_to_kkt_by_rs(self, com="COM1", baudrate=115200):
        logging.debug("Устанавливаем соединение по RS")
        if self.set_connection_settings_to_rs(com, baudrate) != self.fptr.LIBFPTR_OK:
            logging.debug("Не удалось установить настройки драйвера для подключения к ККТ")
            return False
        if self.open() != self.fptr.LIBFPTR_OK:
            logging.debug("Не удалось установить соединение с ККТ")
            return False
        if not self.is_connection_type_rs():
            return False
        logging.debug(
            "Соединение с ККТ установлено по RS. com=[{}] baudrate=[{}]".format(
                com, baudrate
            )
        )
        return True

    def set_connection_settings_to_rs(self, com, baudrate):
        self.fptr.setSingleSetting(
            self.fptr.LIBFPTR_SETTING_MODEL, str(self.fptr.LIBFPTR_MODEL_ATOL_AUTO)
        )
        self.fptr.setSingleSetting(
            self.fptr.LIBFPTR_SETTING_PORT, str(self.fptr.LIBFPTR_PORT_COM)
        )
        self.fptr.setSingleSetting(self.fptr.LIBFPTR_SETTING_COM_FILE, com)
        self.fptr.setSingleSetting(self.fptr.LIBFPTR_SETTING_BAUDRATE, str(baudrate))
        self.fptr.applySingleSettings()
        return self.request_error_code()

    def is_connection_type_rs(self):
        if not self.fptr.isOpened():
            return False
        connection_type = self.fptr.getSingleSetting(self.fptr.LIBFPTR_SETTING_PORT)
        self.request_error_code()
        if not int(connection_type) == self.fptr.LIBFPTR_PORT_COM:
            logging.error(
                "Способ связи с ККТ [{}], а должен быть [RS]".format(connection_type)
            )
            return False
        return True

    def get_model_name(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_DATA_TYPE, self.fptr.LIBFPTR_DT_MODEL_INFO
        )
        self.fptr.queryData()
        model_name = str(self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_MODEL_NAME))
        return model_name

    def set_no_print_flag(self, no_print):
        self.fptr.setParam(self.fptr.LIBFPTR_PARAM_REPORT_ELECTRONICALLY, no_print)
        return True

    def reset_settings(self):
        self.fptr.resetSettings()
        return self.request_error_code()

    def get_fatal_errors_status(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_DATA_TYPE, self.fptr.LIBFPTR_DT_FATAL_STATUS
        )
        self.fptr.queryData()

        self.request_error_code()

        no_serial_number = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_NO_SERIAL_NUMBER
        )
        rtc_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_RTC_FAULT)
        settings_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_SETTINGS_FAULT)
        counter_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_COUNTERS_FAULT)
        user_memory_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_USER_MEMORY_FAULT
        )
        service_counters_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_SERVICE_COUNTERS_FAULT
        )
        attributes_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_ATTRIBUTES_FAULT
        )
        fn_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_FN_FAULT)
        invalid_fn = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_INVALID_FN)
        hard_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_HARD_FAULT)
        memory_manager_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_MEMORY_MANAGER_FAULT
        )
        script_fault = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_SCRIPTS_FAULT)
        wait_for_reboot = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_WAIT_FOR_REBOOT
        )
        universal_counters_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_UNIVERSAL_COUNTERS_FAULT
        )
        commodities_table_fault = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_COMMODITIES_TABLE_FAULT
        )

        return (
            no_serial_number,
            rtc_fault,
            settings_fault,
            counter_fault,
            user_memory_fault,
            service_counters_fault,
            attributes_fault,
            fn_fault,
            invalid_fn,
            hard_fault,
            memory_manager_fault,
            script_fault,
            wait_for_reboot,
            universal_counters_fault,
            commodities_table_fault,
        )

    def reboot_kkt(self):
        self.fptr.deviceReboot()
        return self.request_error_code()

    def set_setting_id(self, _id, _value):
        self.fptr.setParam(self.fptr.LIBFPTR_PARAM_SETTING_ID, _id)
        self.fptr.setParam(self.fptr.LIBFPTR_PARAM_SETTING_VALUE, _value)
        self.fptr.writeDeviceSetting()
        self.request_error_code()
        if self.ErrorCode != self.fptr.LIBFPTR_OK:
            return self.ErrorCode
        self.fptr.commitSettings()
        return self.request_error_code()

    def get_setting_id(self, _id):
        self.fptr.setParam(self.fptr.LIBFPTR_PARAM_SETTING_ID, _id)
        self.fptr.readDeviceSetting()
        self.request_error_code()
        return self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_SETTING_VALUE)

    def print_string(
            self,
            text=None,
            alignment=None,
            wrap=None,
            font=None,
            double_width=None,
            double_height=None,
            linespacing=None,
            brightness=None,
            store_in_journal=None,
    ):
        self.fptr.beginNonfiscalDocument()
        if text is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_TEXT, text)
        if alignment is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_ALIGNMENT, alignment)
        if wrap is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_TEXT_WRAP, wrap)
        if font is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_FONT, font)
        if double_width is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_FONT_DOUBLE_WIDTH, double_width)
        if double_height is not None:
            self.fptr.setParam(
                self.fptr.LIBFPTR_PARAM_FONT_DOUBLE_HEIGHT, double_height
            )
        if linespacing is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_LINESPACING, linespacing)
        if brightness is not None:
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_BRIGHTNESS, brightness)
        if store_in_journal is not None:
            self.fptr.setParam(
                self.fptr.LIBFPTR_PARAM_STORE_IN_JOURNAL, store_in_journal
            )
        self.fptr.printText()
        self.fptr.endNonfiscalDocument()
        return self.request_error_code()

    def print_custom_text(self, text_tuple: tuple):
        """
        Метод печати нефискального текста на ЧЛ
        """
        self.fptr.open()
        self.fptr.beginNonfiscalDocument()
        for text in text_tuple:
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, text)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_ALIGNMENT, 0)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, 0)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_FONT, 0)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_FONT_DOUBLE_HEIGHT, False)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_FONT_DOUBLE_WIDTH, False)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_FORMAT_TEXT, False)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_LINESPACING, 0)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_BRIGHTNESS, 0)
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_STORE_IN_JOURNAL, True)
            self.fptr.printText()
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_PRINT_FOOTER, False)
        self.fptr.endNonfiscalDocument()
        self.fptr.close()

    def get_fn_info(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_FN_DATA_TYPE, self.fptr.LIBFPTR_FNDT_FN_INFO
        )
        self.fptr.fnQueryData()
        self.request_error_code()

        serial = self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        version = self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_FN_VERSION)
        type = self.fptr.getParamInt(self.fptr.LIBFPTR_PARAM_FN_TYPE)
        state = self.fptr.getParamInt(self.fptr.LIBFPTR_PARAM_FN_STATE)
        flags = self.fptr.getParamInt(self.fptr.LIBFPTR_PARAM_FN_FLAGS)

        need_replacement = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_FN_NEED_REPLACEMENT
        )
        exhausted = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_FN_RESOURCE_EXHAUSTED
        )
        memory_overflow = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_FN_MEMORY_OVERFLOW
        )
        ofd_timeout = self.fptr.getParamBool(self.fptr.LIBFPTR_PARAM_FN_OFD_TIMEOUT)
        critical_error = self.fptr.getParamBool(
            self.fptr.LIBFPTR_PARAM_FN_CRITICAL_ERROR
        )

        return (
            serial,
            version,
            type,
            state,
            flags,
            need_replacement,
            exhausted,
            memory_overflow,
            ofd_timeout,
            critical_error,
        )

    def init_mgm(self):
        self.fptr.initMgm()
        return self.request_error_code()

    def get_last_doc_with_template(self, tempalate, variable_settings=None):
        last_fn_doc_number = self.get_last_fiscal_document_number()
        last_fn_doc_str = None
        for _ in range(3):
            request_last_fn_doc = (
                    '{"type": "getFnDocument", "fiscalDocumentNumber": %i}'
                    % last_fn_doc_number
            )
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_JSON_DATA, request_last_fn_doc)
            self.fptr.processJson()
            last_fn_doc_str = self.fptr.getParamString(
                self.fptr.LIBFPTR_PARAM_JSON_DATA
            )
            if last_fn_doc_str != "":
                break
        last_fn_doc_dic = json.loads(str(last_fn_doc_str))
        last_fn_doc_dic = last_fn_doc_dic["documentTLV"]
        logging.info(
            "\nФД %s, JSON из ФН: %s"
            % (
                str(last_fn_doc_number),
                json.dumps(
                    last_fn_doc_dic, sort_keys=True, indent=4, ensure_ascii=False
                ),
            )
        )

        return last_fn_doc_dic

    def execute_json(self, json_task, timeout=30):
        logging.debug(f"execute_json() < json_task {json_task=}, timeout {timeout=}")
        logging.info(f"execute_json() < json_task {json_task=}, timeout {timeout=}")  # временно, нужно для отладки
        try:
            self.fptr.open()
            self.fptr.setParam(self.fptr.LIBFPTR_PARAM_JSON_DATA, json.dumps(json_task))
            self.fptr.processJson()
            response_raw = self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_JSON_DATA)
            logging.info(f"execute_json() > {response_raw=}")
            if response_raw is not None:
                try:
                    response = json.loads(response_raw)
                    logging.debug(f"execute_json() > {response=}")
                    logging.info(f"execute_json() > {response=}")
                    return response
                except json.decoder.JSONDecodeError as e:
                    logging.error(
                        f"[ERROR] error with json.loads from response: {e}"
                    )
        except ValueError as error:
            logging.error(f"{inspect.currentframe().f_code.co_name}: {error}")
        finally:
            self.fptr.close()  # Закрытие ДТО
        logging.debug(f"execute_json() > None")
        logging.info(f"execute_json() > None")
        return None

    def get_fn_number(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_DATA_TYPE, self.fptr.LIBFPTR_DT_CACHE_REQUISITES
        )
        self.fptr.queryData()

        serialNumber = self.fptr.getParamString(
            self.fptr.LIBFPTR_PARAM_FN_SERIAL_NUMBER
        )
        return serialNumber

    def get_rnm_number(self):
        self.fptr.setParam(
            self.fptr.LIBFPTR_PARAM_DATA_TYPE, self.fptr.LIBFPTR_DT_CACHE_REQUISITES
        )
        self.fptr.queryData()

        ecrRegNumber = self.fptr.getParamString(
            self.fptr.LIBFPTR_PARAM_ECR_REGISTRATION_NUMBER
        )

        return ecrRegNumber

    def get_not_sent_fd_qty(self):
        logging.debug(f"get_not_sent_fd_qty()")
        task = {"type": "ofdExchangeStatus"}
        ofdExchangeStatus = self.execute_json(task)
        if ofdExchangeStatus is not None:
            not_sent_fd_qty = ofdExchangeStatus["status"]["notSentCount"]
            logging.debug(f"get_not_sent_fd_qty() %s", not_sent_fd_qty)
            return not_sent_fd_qty
        logging.debug(f"get_not_sent_fd_qty() None")
        return None

    def wait_for_sent_all_fd(self, timeout: int = 600):
        logging.debug(f"wait_for_sent_all_fd() timeout %s", timeout)
        start_time = time.time()
        while self.get_not_sent_fd_qty() != 0:
            if time.time() - start_time > timeout:
                logging.debug(f"get_not_sent_fd_qty() False")
                return False
            time.sleep(3)
        logging.debug(f"get_not_sent_fd_qty() True")
        return True

    def process_json(self, json_task, answer_indent=4, flag_all_kkt_settings=False):
        self.fptr.setParam(self.fptr.LIBFPTR_PARAM_JSON_DATA, json_task)
        self.fptr.processJson()
        error = self.request_error_code(flag_all_kkt_settings=flag_all_kkt_settings)
        json_str_answer = self.fptr.getParamString(self.fptr.LIBFPTR_PARAM_JSON_DATA)
        if json_str_answer != "":
            self.JsonAnswer = None
            try:
                self.JsonAnswer = json.dumps(
                    json.loads(json_str_answer),
                    ensure_ascii=False,
                    indent=answer_indent,
                )
            except ValueError as error:
                logging.error(f"{inspect.currentframe().f_code.co_name}: {error}")
        return error

    def execute_mass_json(self, json_task, quantity, timeout=30):
        logging.debug(f"execute_json() < json_task {json_task}, timeout {timeout}")
        logging.debug(f"execute_json() < json_task {json_task}, timeout {timeout}")
        try:
            if not self.is_connected():
                if not self.wait_to_connect(timeout=timeout):
                    return False
            self.fptr.open()
            count = 0
            while count < quantity:
                self.fptr.setParam(
                    self.fptr.LIBFPTR_PARAM_JSON_DATA, json.dumps(json_task)
                )
                self.fptr.processJson()
                logging.debug(count)
                count += 1
        except:
            logging.error("Exception in execute_json():")
        finally:
            self.fptr.close()  # Закрытие ДТО
        logging.debug(f"execute_json() > None")
        return None

    def is_connected(self, timeout=5):
        logging.debug("ККТ is_connected() timeout %s", timeout)
        connected = False

        def check_connection():
            nonlocal connected
            self.fptr.open()
            if self.fptr.isOpened():
                self.fptr.close()
                logging.debug("ККТ is_connected() True")
                connected = True
            self.fptr.close()

        timer = threading.Timer(timeout, check_connection)
        timer.start()

        while not connected and timer.is_alive():
            time.sleep(0.1)

        timer.cancel()

        logging.debug("ККТ is_connected() %s", connected)
        return connected

    def wait_to_connect(self, timeout=300):
        logging.debug(f"wait_to_connect() timeout={timeout}")
        start_time = time.time()
        while not self.is_connected() and not time.time() - start_time > timeout:
            logging.debug(
                f"Не получен ответ от ККТ, time {time.time() - start_time} timeout {timeout}"
            )
        if self.is_connected():
            logging.debug("ККТ доступна")
            return True
        logging.debug("ККТ не отвечает")
        return False

    def print_info_report(self):
        self.fptr.open()
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, 5)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_ELECTRONICALLY, 0)
        self.fptr.report()

    def get_TPG_count(self) -> int:
        """
        Получить ресурс ТПГ (постоянный)
        """
        self.fptr.open()
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_TERMAL_RESOURCE)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_COUNTER_TYPE, IFptr.LIBFPTR_CT_ROLLUP)
        self.fptr.queryData()
        count = self.fptr.getParamInt(IFptr.LIBFPTR_PARAM_COUNT)

        if count == 0:
            self.print_info_report()

        return count

    def get_TPG_temperature(self):
        """
        Получить температуру ТПГ
        """
        self.fptr.open()

        self.fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_PRINTER_TEMPERATURE)
        self.fptr.queryData()

        temperature = self.fptr.getParamString(IFptr.LIBFPTR_PARAM_PRINTER_TEMPERATURE)
        return temperature

    def get_TPG_motor_count(self):
        """
        Получить ресурс шагового двигателя
        """
        self.fptr.open()

        self.fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STEP_RESOURCE)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_COUNTER_TYPE, IFptr.LIBFPTR_CT_ROLLUP)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_STEP_COUNTER_TYPE, IFptr.LIBFPTR_SCT_OVERALL)
        self.fptr.queryData()

        count = self.fptr.getParamInt(IFptr.LIBFPTR_PARAM_COUNT)

        return count

    def get_registration_data(self):
        """
        Метод запрашивает информацию о регистрации и записывает в атрибуты класса
        organization	Информация об организации	object
        name	Название организации (тег 1048)	string
        vatin	ИНН организации (тег 1018)	string
        email	E-mail организации (адрес отравителя электронных чеков) (тег 1117)	string
        address	Адрес расчетов (тег 1009)	string
        taxationTypes	Список систем налогообложения (тег 1062)	string[]	osn - общая
        usnIncome - упрощенная доход
        usnIncomeOutcome - упрощенная доход минус расход
        esn - единый сельскохозяйственный налог
        patent - патентная система налогообложения
        agents	Признак агента (тег 1057)	string[]	bankPayingAgent - банковский платежный агент
        bankPayingSubagent - банковский платежный субагент
        payingAgent - платежный агент
        payingSubagent - платежный субагент
        attorney - поверенный
        commissionAgent - комиссионер
        another - другой тип агента	по умолчанию - пустой список (не устанавливать флаги агентов)

        device	Параметры ККТ	object
        registrationNumber	Регистрационный номер ККТ (тег 1037)	string
        fnsUrl	Адрес сайта ФНС (тег 1060)	string
        offlineMode	Признак автономного режима (тег 1002)	bool
        machineInstallation	Признак установки принтера в автомате (тег 1221)	bool
        bso	Признак АС БСО (тег 1110)	bool
        encryption	Признак шифрования (тег 1056)	bool
        autoMode	Признак автоматического режима (тег 1001)	bool
        machineNumber	Номер автомата (тег 1036)	string
        internet	Признак ККТ для расчетов только в Интернет (тег 1108)	bool
        service	Признак расчетов за услуги (тег 1109)	bool
        excise	Продажа подакцизного товара (тег 1207)	bool
        gambling	Признак проведения азартных игр (тег 1193)	bool
        lottery	Признак проведения лотереи (тег 1126)	bool
        defaultTaxationType	СНО по умолчанию (тег 1055)	string	osn - общая
        usnIncome - упрощенная доход
        usnIncomeOutcome - упрощенная доход минус расход
        esn - единый сельскохозяйственный налог
        patent - патентная система налогообложения	Можно не указывать, если taxationTypes имеет 1 элемент, иначе должен входить в список taxationTypes
        ofdChannel	Канал обмена с ОФД	string	usb - USB (EoU)
        ethernet - Ethernet
        wifi - Wi-Fi
        gsm - GSM-модем
        proto - средствами протокола ККТ
        tcpipOsStack - TCP/IP стек ОС
        ffdVersion	Версия ФФД (тег 1209)	string	1.05
                                                    1.1
                                                    1.2
        paymentsAddress	Место расчетов (тег 1187)	string
        insurance	Признак осуществления страховой деятельности	bool
        marking	Признак торговли маркированными товарами	bool
        pawnShop	Признак осуществления ломбардной деятельности	bool

        ofd	Параметры ОФД	object
        name	Название ОФД (тег 1046)	string
        vatin	ИНН ОФД (тег 1017)	string
        host	Адрес ОФД	string
        port	Порт ОФД	number	0 - 65535
        dns	DNS ОФД	string
        """

        registration_info = self.execute_json(json_task={
            "type": "getRegistrationInfo"
        })

        if registration_info is None:
            return
        try:
            if not registration_info:
                return

            # device
            if 'device' in registration_info.keys():
                self.device = registration_info['device']
            if 'autoMode' in self.device.keys():
                self.autoMode = self.device['autoMode']
            if 'bso' in self.device.keys():
                self.bso = self.device['bso']
            if 'defaultTaxationType' in self.device.keys():
                self.defaultTaxationType = self.device['defaultTaxationType']
            if 'encryption' in self.device.keys():
                self.encryption = self.device['encryption']
            if 'excise' in self.device.keys():
                self.excise = self.device['excise']
            if 'ffdVersion' in self.device.keys():
                self.ffdVersion = self.device['ffdVersion']
            if 'fnsUrl' in self.device.keys():
                self.fnsUrl = self.device['fnsUrl']
            if 'gambling' in self.device.keys():
                self.gambling = self.device['gambling']
            if 'internet' in self.device.keys():
                self.internet = self.device['internet']
            if 'lottery' in self.device.keys():
                self.lottery = self.device['lottery']
            if 'machineInstallation' in self.device.keys():
                self.machineInstallation = self.device['machineInstallation']
            if 'machineNumber' in self.device.keys():
                self.machineNumber = self.device['machineNumber']
            if 'ofdChannel' in self.device.keys():
                self.ofdChannel = self.device['ofdChannel']
            if 'offlineMode' in self.device.keys():
                self.offlineMode = self.device['offlineMode']
            if 'paymentsAddress' in self.device.keys():
                self.paymentsAddress = self.device['paymentsAddress']
            if 'registrationNumber' in self.device.keys():
                self.registrationNumber = self.device['registrationNumber']
            if 'service' in self.device.keys():
                self.service = self.device['service']

            # ofd
            if 'ofd' in registration_info.keys():
                self.ofd = registration_info['ofd']
            if 'dns' in self.ofd.keys():
                self.dns = self.ofd['dns']
            if 'host' in self.ofd.keys():
                self.host = self.ofd['host']
            if 'name' in self.ofd.keys():
                self.name = self.ofd['name']
            if 'port' in self.ofd.keys():
                self.port = self.ofd['port']
            if 'vatin' in self.ofd.keys():
                self.vatin = self.ofd['vatin']

            # organization
            if 'organization' in registration_info.keys():
                self.organization = registration_info['organization']
            if 'address' in self.organization.keys():
                self.address = self.organization['address']
            if 'agents' in self.organization.keys():
                self.agents = self.organization['agents']
            if 'email' in self.organization.keys():
                self.email = self.organization['email']
            if 'name' in self.organization.keys():
                self.name = self.organization['name']
            if 'taxationTypes' in self.organization.keys():
                self.taxationTypes = self.organization['taxationTypes']
            if 'vatin' in self.organization.keys():
                self.vatin = self.organization['vatin']
            self.fptr.close()
        except KeyError as error:
            self.fptr.close()
            logging.error(f"{inspect.currentframe().f_code.co_name}: {error}")

    def get_fn_data(self):
        """
        Метод запрашивает информацию о ФН и записывает в атрибуты класса.
        Информация о ФН (fnInfo)
        serial	Заводской номер ФН	string
        version	Версия ФН	string
        execution	Исполнение ФН (только для ФН-М)	string
        numberOfRegistrations	Количество проведенных регистраций	number
        registrationsRemaining	Количество оставшихся регистраций	number
        validityDate	Срок действия ФН	string
        ffdVersion	Версия ФФД ККТ	string
        fnFfdVersion	Версия ФФД ФН	string
        livePhase	Фаза жизни ФН.
        Принимает значения:
        init - настройка ФН
        configured - настроен, готов в активации
        fiscalMode - фискальный режим
        postFiscalMode - постфискальный режим
        accessArchive - доступ к архиву ФН
        unknown - неизвестная фаза жизни	string
        Предупреждения ФН (fnInfo.warnings)
        memoryOverflow	Память ФН переполнена	bool
        needReplacement	Требуется срочная замена ФН	bool
        ofdTimeout	Превышено время ожидания ответа от ОФД	bool
        resourceExhausted	Исчерпан ресурс ФН	bool
        criticalError	Критическая ошибка ФН	bool
        fnContainsKeysUpdaterServerUri	ФН содержит URI сервера ОКП	bool
        """
        self.fptr.open()
        fn_info = self.execute_json(json_task={
            "type": "getFnInfo"
        })
        if fn_info is None:
            return
        try:
            if 'execution' in fn_info['fnInfo']:
                self.fnExecution = fn_info['fnInfo']['execution']
            if 'ffdVersion' in fn_info['fnInfo']:
                self.FfdVersion = fn_info['fnInfo']['ffdVersion']
            if 'fnContainsKeysUpdaterServerUri' in fn_info['fnInfo']:
                self.fnContainsKeysUpdaterServerUri = fn_info['fnInfo']['fnContainsKeysUpdaterServerUri']
            if 'fnFfdVersion' in fn_info['fnInfo']:
                self.fnFfdVersion = fn_info['fnInfo']['fnFfdVersion']
            if 'livePhase' in fn_info['fnInfo']:
                self.fnLivePhase = fn_info['fnInfo']['livePhase']
            if 'numberOfRegistrations' in fn_info['fnInfo']:
                self.fnNumberOfRegistrations = fn_info['fnInfo']['numberOfRegistrations']
            if 'registrationsRemaining' in fn_info['fnInfo']:
                self.fnRegistrationsRemaining = fn_info['fnInfo']['registrationsRemaining']
            if 'serial' in fn_info['fnInfo']:
                self.fnSerial = fn_info['fnInfo']['serial']
            if 'validityDate' in fn_info['fnInfo']:
                self.fnValidityDate = fn_info['fnInfo']['validityDate']
            if 'version' in fn_info['fnInfo']:
                self.fnVersion = fn_info['fnInfo']['version']
            if 'warnings' in fn_info['fnInfo']:
                self.fnWarnings = fn_info['fnInfo']['warnings']
            self.fptr.close()
        except KeyError as error:
            self.fptr.close()
            logging.error(f"{inspect.currentframe().f_code.co_name}: {error}")

    def set_device_parameters(self, params: dict):
        """
        Метод записи настроек ККТ
        params: dict, словарь параметров
        """
        params_list = []
        for key, value in params.items():
            temp_dict = {'key': int(key), 'value': str(value)}
            params_list.append(temp_dict)

        task = {
            "type": "setDeviceParameters",
            "deviceParameters": params_list
        }
        try:
            self.execute_json(task)
        except Exception as error:
            logging.error(f"{inspect.currentframe().f_code.co_name}: {error}")
