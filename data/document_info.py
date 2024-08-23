from typing import Dict, List

def load_document_dict(pre_processing:bool) -> List[Dict]:
    if pre_processing:
        documents_list = [
                                dict(
                                    documents_path = "data/pre_documents",
                                    document_name="전처리완료_(221115 수정배포) (2022.10) 금융분야 마이데이터 기술 가이드라인.xlsx",
                                    source="금융분야 마이데이터 기술 가이드라인(https://www.mydatacenter.or.kr:3441/myd/bbsctt/normal1/normal/cb202bf2-9cb7-4205-9c1e-83d6cc39ebe0/39/bbsctt.do)-{page}페이지",
                                    category="guideline",
                                    reg_date=20240822,
                                    edit_date=20221115,
                                    custom_patterns=[],
                                    origin="(221115 수정배포) (2022.10) 금융분야 마이데이터 기술 가이드라인.pdf"
                                ),
                               dict(
                                    documents_path = "data/pre_documents",
                                    document_name="3장까지_(수정게시) 금융분야 마이데이터 표준 API 규격_v1.xlsx",
                                    source = "금융분야 마이데이터 표준 API 규격 v1.pdf(https://www.mydatacenter.or.kr:3441/myd/bbsctt/normal1/normal/20737b67-6594-4766-978d-fd766b8ed568/4/bbsctt.do)-{page}페이지",
                                    category="baseline",
                                    reg_date=20240822,
                                    edit_date=20210930,
                                    custom_patterns=[],
                                    origin="(수정게시) 금융분야 마이데이터 표준 API 규격 v1.pdf",
                                )
        ]
    else:
        documents_list = [
                            dict(
                                documents_path = "data/documents",
                                document_name="(221115 수정배포) (2022.10) 금융분야 마이데이터 기술 가이드라인.pdf",
                                start_page=9, 
                                end_page=136,
                                source="금융분야 마이데이터 기술 가이드라인(https://www.mydatacenter.or.kr:3441/myd/bbsctt/normal1/normal/cb202bf2-9cb7-4205-9c1e-83d6cc39ebe0/39/bbsctt.do)-{page}페이지",
                                category="document",
                                reg_date=20240822,
                                edit_date=20221115,
                                custom_patterns=[r"금융분야 마이데이터 기술 가이드라인[\n]{0,1}", 
                                                 r"[0-9\s]+금융보안원[\n]{0,1}", 
                                                 r"Financial Security Institute [0-9]{1,3}[\n]{0,1}", 
                                                 r"[1장. 개요|2장. 개인신용정보 전송|3장. 마이데이터서비스|4장. 마이데이터 본인인증|5장. 마이데이터 보안|6장. Q&A|7장. 참고]+[\n]{0,1}"],
                                origin="(221115 수정배포) (2022.10) 금융분야 마이데이터 기술 가이드라인.pdf"
                            ),
                           dict(
                                documents_path = "data/documents",
                                document_name="(수정게시) 금융분야 마이데이터 표준 API 규격 v1.pdf",
                                start_page=26, 
                                source = "금융분야 마이데이터 표준 API 규격 v1.pdf(https://www.mydatacenter.or.kr:3441/myd/bbsctt/normal1/normal/20737b67-6594-4766-978d-fd766b8ed568/4/bbsctt.do)-{page}페이지",
                                category="document",
                                reg_date=20240822,
                                edit_date=20210930,
                                custom_patterns=[r"금융분야 마이데이터 표준API 규격[\n\s]+", r"금융보안원 www.fsec.or.kr - [0-9]{1,3} -"],
                                origin="(수정게시) 금융분야 마이데이터 표준 API 규격 v1.pdf"
                            )
        ]
    return documents_list