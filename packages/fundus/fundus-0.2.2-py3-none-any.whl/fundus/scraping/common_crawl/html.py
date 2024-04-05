from typing import Dict, Iterator, Optional
from urllib.parse import urlparse

import chardet
import requests
from fastwarc import ArchiveIterator, WarcRecord, WarcRecordType

from fundus.logging import basic_logger
from fundus.publishers.base_objects import PublisherEnum
from fundus.scraping.filter import URLFilter
from fundus.scraping.html import HTML, WarcSource, _default_header


class CCNewsSource:
    def __init__(self, *publishers: PublisherEnum, warc_path: str, headers: Optional[Dict[str, str]] = None):
        self.publishers = publishers
        self.warc_path = warc_path
        self.headers = headers or _default_header

        self._publisher_mapping: Dict[str, PublisherEnum] = {
            urlparse(publisher.domain).netloc: publisher for publisher in publishers
        }

    def fetch(self, url_filter: Optional[URLFilter] = None) -> Iterator[HTML]:
        def extract_content(record: WarcRecord) -> Optional[str]:
            warc_body: bytes = record.reader.read()

            try:
                return str(warc_body, encoding=record.http_charset)
            except (UnicodeDecodeError, TypeError):
                encoding: Optional[str] = chardet.detect(warc_body)["encoding"]

                if encoding is not None:
                    basic_logger.debug(
                        f"Trying to decode record {record.record_id!r} from {target_url!r} "
                        f"using detected encoding {encoding}."
                    )

                    try:
                        return str(warc_body, encoding=encoding)
                    except UnicodeDecodeError:
                        basic_logger.warning(
                            f"Couldn't decode record {record.record_id!r} from {target_url!r} with "
                            f"original charset {record.http_charset!r} using detected charset {encoding!r}."
                        )
                else:
                    basic_logger.warning(
                        f"Couldn't detect charset for record {record.record_id!r} from {target_url!r} "
                        f"with invalid original charset {record.http_charset!r}."
                    )

            return None

        with requests.Session() as session:
            stream = session.get(self.warc_path, stream=True, headers=self.headers).raw

            for warc_record in ArchiveIterator(stream, record_types=WarcRecordType.response, verify_digests=True):
                target_url = str(warc_record.headers["WARC-Target-URI"])

                if url_filter is not None and url_filter(target_url):
                    basic_logger.debug(f"Skipped WARC record with target URI {target_url!r} because of URL filter")
                    continue

                publisher_domain: str = urlparse(target_url).netloc

                if publisher_domain not in self._publisher_mapping:
                    continue

                publisher = self._publisher_mapping[publisher_domain]

                if publisher.url_filter is not None and publisher.url_filter(target_url):
                    basic_logger.debug(
                        f"Skipped WARC record with target URI {target_url!r} because of "
                        f"publisher specific URL filter"
                    )
                    continue

                if (content := extract_content(warc_record)) is None:
                    continue

                yield HTML(
                    requested_url=target_url,
                    responded_url=target_url,
                    content=content,
                    crawl_date=warc_record.record_date,
                    source=WarcSource(
                        publisher=publisher.publisher_name,
                        warc_path=self.warc_path,
                        warc_headers=dict(warc_record.headers),
                        http_headers=dict(warc_record.http_headers),
                    ),
                )
