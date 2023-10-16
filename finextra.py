"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from datetime import timedelta, datetime

import dateparser
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from src.spp.types import SPP_document
import warnings

# Ignore dateparser warnings regarding pytz
# https://github.com/scrapinghub/dateparser/issues/1013#issuecomment-956302959
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class FINEXTRA:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'finextra'
    HOST = "https://www.finextra.com"
    _content_document: list[SPP_document]

    def __init__(self, driver, interval: timedelta, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        self.driver = driver
        self.interval = interval

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        current_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        end_date = current_date - self.interval
        self.logger.info(f"Текущая дата: {datetime.strftime(current_date, '%Y-%m-%d')}")
        self.logger.info(
            f"Окончательная дата: {datetime.strftime(end_date, '%Y-%m-%d')} (разница в днях: {self.interval})")

        while True:
            page_link = f"https://www.finextra.com/latest-news?date={datetime.strftime(current_date, '%Y-%m-%d')}"
            try:
                self.logger.info(f'Загрузка: {page_link}')
                self.driver.get(page_link)
            except:
                self.logger.info('TimeoutException:',
                                 f"https://www.finextra.com/latest-news?date={datetime.strftime(current_date, '%Y-%m-%d')}")
                current_date = current_date - timedelta(1)
                self.logger.debug(f"Изменение даты на новую: {datetime.strftime(current_date, '%Y-%m-%d')}")
                continue
            time.sleep(1)

            # Цикл по новостям за определенную дату
            while True:
                articles = self.driver.find_elements(By.XPATH, '//*[@class=\'modulegroup--latest-storylisting\']//h4/a')

                for article in articles:
                    article_url = article.get_attribute('href')

                    self.logger.info(f'Загрузка и обработка документа: {article_url}')
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[1])

                    try:
                        self.driver.get(article_url)
                    except TimeoutException:
                        self.logger.info(f'TimeoutException: {article_url}')
                        self.logger.info('Закрытие вкладки и переход к след. материалу...')
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue

                    time.sleep(1)

                    try:
                        article_title = self.driver.find_element(By.CLASS_NAME, 'article--title')
                        article_type = self.driver.current_url.split('/')[3]
                        title = article_title.find_element(By.TAG_NAME, 'h1').text
                        date_text = article_title.find_element(By.CLASS_NAME, 'time--diff').text

                        date = dateparser.parse(date_text)
                        tw_count = article_title.find_element(By.CLASS_NAME, 'module--share-this').find_element(By.ID,
                                                                                                                'twitterResult').text
                        li_count = article_title.find_element(By.CLASS_NAME, 'module--share-this').find_element(By.ID,
                                                                                                                'liResult').text
                        fb_count = article_title.find_element(By.CLASS_NAME, 'module--share-this').find_element(By.ID,
                                                                                                                'fbResult').text

                        left_tags = self.driver.find_element(By.CLASS_NAME, 'article--tagging-left')

                        try:
                            related_comp = ', '.join([el.text for el in left_tags.find_elements(By.XPATH,
                                                                                                '//h4[text() = \'Related Companies\']/following-sibling::div[1]//span')
                                                      if el.text != ''])
                        except:
                            related_comp = ''

                        try:
                            lead_ch = ', '.join([el.text for el in left_tags.find_elements(By.XPATH,
                                                                                           '//h4[text() = \'Lead Channel\']/following-sibling::div[1]//span')
                                                 if el.text != ''])
                            logging_string = f'{lead_ch} - {title}'
                            self.logger.info(logging_string.replace('[^\dA-Za-z]', ''))
                        except:
                            lead_ch = ''

                        try:
                            channels = ', '.join([el.text for el in left_tags.find_elements(By.XPATH,
                                                                                            '//h4[text() = \'Channels\']/following-sibling::div[1]//span')
                                                  if el.text != ''])
                        except:
                            channels = ''

                        try:
                            keywords = ', '.join([el.text for el in left_tags.find_elements(By.XPATH,
                                                                                            '//h4[text() = \'Keywords\']/following-sibling::div[1]//span')
                                                  if el.text != ''])
                        except:
                            keywords = ''

                        try:
                            category_name = \
                                left_tags.find_element(By.CLASS_NAME, 'category--title').find_element(By.TAG_NAME,
                                                                                                      'span').get_attribute(
                                    'innerHTML').split(' |')[0]
                            category_desc = left_tags.find_element(By.CLASS_NAME, 'category--meta').get_attribute(
                                'innerHTML')
                        except:
                            category_name = ''
                            category_desc = ''

                        abstract = self.driver.find_element(By.CLASS_NAME, 'article--body').find_element(By.CLASS_NAME,
                                                                                                         'stand-first').text
                        text = self.driver.find_element(By.CLASS_NAME, 'article--body').text
                        comment_count = self.driver.find_element(By.ID, 'comment').find_element(By.XPATH,
                                                                                                './following-sibling::h4').text.split()[
                            1].split('(', 1)[1].split(')')[0]

                        document = SPP_document(
                            doc_id=None,
                            title=title,
                            abstract=abstract,
                            text=text,
                            web_link=article_url,
                            local_link=None,
                            other_data={
                                'article_type': article_type,
                                'related_comp': related_comp,
                                'lead_ch': lead_ch,
                                'channels': channels,
                                'keywords': keywords,
                                'category_name': category_name,
                                'category_desc': category_desc,
                                'tw_count': tw_count,
                                'li_count': li_count,
                                'fb_count': fb_count,
                                'comment_count': comment_count,
                            },
                            pub_date=date,
                            load_date=None
                        )
                        self._find_document_text_for_logger(document)
                        self._content_document.append(document)

                    except:
                        self.logger.exception(f'Ошибка при обработке: {article_url}')
                        self.logger.info('Закрытие вкладки и переход к след. материалу...')
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                try:
                    pagination = self.driver.find_element(By.ID, 'pagination')
                    next_page_url = pagination.find_element(By.XPATH, '//*[text() = \'›\']').get_attribute('href')
                    self.driver.get(next_page_url)
                except Exception as e:
                    self.logger.info('Пагинация не найдена. Прерывание обработки страницы')
                    break

            current_date = current_date - timedelta(1)
            self.logger.info(f"Изменение даты на новую: {datetime.strftime(current_date, '%Y-%m-%d')}")

            if current_date < end_date:
                self.logger.info('Текущая дата меньше окончательной даты. Прерывание парсинга.')
                break
        # Логирование найденного документа
        # self.logger.info(self._find_document_text_for_logger(document))

        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
