from sqlalchemy import Column, Integer, String
from backend.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True) # ID unique e.g., NQ_69_2025
    so_hieu = Column(String, index=True)
    ten = Column(String)
    loai = Column(String, index=True)
    co_quan = Column(String)
    ngay_hieu_luc = Column(String)
    tinh_trang = Column(String)
    file_path = Column(String) # Đường dẫn tới file raw gốc
