"""
Dữ liệu mẫu văn bản pháp luật lĩnh vực Chứng khoán.
"""
import json, os

SAMPLE_DOCS = [
    {
        "id": "LUAT_CK_2019",
        "so_hieu": "54/2019/QH14",
        "ten": "Luật Chứng khoán 2019",
        "loai": "Luật",
        "co_quan": "Quốc hội",
        "ngay_ban_hanh": "2019-11-26",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Luật này quy định các hoạt động về chứng khoán và thị trường chứng khoán; quyền và nghĩa vụ của tổ chức, cá nhân có liên quan đến hoạt động chứng khoán và thị trường chứng khoán.

Điều 2. Đối tượng áp dụng
Luật này áp dụng đối với tổ chức, cá nhân Việt Nam và tổ chức, cá nhân nước ngoài tham gia đầu tư chứng khoán và hoạt động trên thị trường chứng khoán Việt Nam.

Điều 4. Giải thích từ ngữ
1. Chứng khoán là tài sản, bao gồm: cổ phiếu, trái phiếu, chứng chỉ quỹ, chứng quyền, quyền mua cổ phần, chứng chỉ lưu ký, chứng khoán phái sinh.
2. Cổ phiếu là loại chứng khoán xác nhận quyền và lợi ích hợp pháp của người sở hữu đối với một phần vốn cổ phần của tổ chức phát hành.
3. Trái phiếu là loại chứng khoán xác nhận quyền và lợi ích hợp pháp của người sở hữu đối với một phần nợ của tổ chức phát hành.

Điều 15. Chào bán chứng khoán ra công chúng
1. Chào bán cổ phiếu ra công chúng bao gồm: chào bán cổ phiếu lần đầu ra công chúng, chào bán thêm cổ phiếu ra công chúng.
2. Điều kiện chào bán cổ phiếu lần đầu ra công chúng: vốn điều lệ đã góp tại thời điểm đăng ký chào bán từ 30 tỷ đồng trở lên; hoạt động kinh doanh của 02 năm liên tục liền trước năm đăng ký chào bán phải có lãi.

Điều 31. Niêm yết chứng khoán
Tổ chức phát hành đăng ký niêm yết chứng khoán tại Sở giao dịch chứng khoán Việt Nam phải đáp ứng điều kiện: là công ty cổ phần; đáp ứng điều kiện về vốn, hoạt động kinh doanh.

Điều 41. Công ty chứng khoán
Công ty chứng khoán được thực hiện một, một số hoặc toàn bộ nghiệp vụ kinh doanh: Môi giới chứng khoán, Tự doanh chứng khoán, Bảo lãnh phát hành chứng khoán, Tư vấn đầu tư chứng khoán.

Điều 56. Quỹ đầu tư chứng khoán
Quỹ đầu tư chứng khoán được tổ chức và hoạt động dưới hình thức quỹ mở, quỹ đóng, quỹ hoán đổi danh mục, quỹ đầu tư bất động sản.""",
        "lien_quan": ["ND_155_2020", "TT_118_2020", "TT_119_2020", "QD_22_2023"]
    },
    {
        "id": "ND_155_2020",
        "so_hieu": "155/2020/NĐ-CP",
        "ten": "Nghị định 155/2020/NĐ-CP hướng dẫn Luật Chứng khoán",
        "loai": "Nghị định",
        "co_quan": "Chính phủ",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực (sửa đổi bởi NĐ 128/2024)",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Nghị định này quy định chi tiết thi hành một số điều của Luật Chứng khoán số 54/2019/QH14.

Điều 9. Điều kiện chào bán cổ phiếu lần đầu ra công chúng
Tổ chức phát hành thực hiện chào bán cổ phiếu lần đầu ra công chúng khi đáp ứng đủ các điều kiện: vốn điều lệ đã góp từ 30 tỷ đồng trở lên; kết quả hoạt động kinh doanh 02 năm liên tục phải có lãi; không có lỗ lũy kế.

Điều 43. Thành viên giao dịch
Thành viên giao dịch của Sở giao dịch chứng khoán Việt Nam là công ty chứng khoán được cấp phép thực hiện nghiệp vụ môi giới chứng khoán.

Điều 110. Thuế thu nhập từ chuyển nhượng chứng khoán
Thuế suất thuế thu nhập cá nhân từ chuyển nhượng chứng khoán là 0,1% trên giá bán chứng khoán.

Điều 135. Xử phạt vi phạm hành chính
Vi phạm quy định về công bố thông tin bị phạt tiền từ 50 triệu đến 100 triệu đồng.""",
        "lien_quan": ["LUAT_CK_2019", "ND_128_2024"]
    },
    {
        "id": "ND_128_2024",
        "so_hieu": "128/2024/NĐ-CP",
        "ten": "Nghị định 128/2024/NĐ-CP sửa đổi Nghị định 155/2020",
        "loai": "Nghị định",
        "co_quan": "Chính phủ",
        "ngay_ban_hanh": "2024-10-08",
        "ngay_hieu_luc": "2024-11-25",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Sửa đổi một số điều của Nghị định 155/2020/NĐ-CP
Nghị định này sửa đổi, bổ sung một số điều của Nghị định 155/2020/NĐ-CP quy định chi tiết thi hành Luật Chứng khoán.

Sửa đổi Điều 9: Bổ sung điều kiện về quản trị công ty, yêu cầu tổ chức phát hành phải có cơ cấu cổ đông đa dạng.

Sửa đổi Điều 43: Nâng cao tiêu chuẩn thành viên giao dịch, yêu cầu vốn điều lệ tối thiểu cao hơn.""",
        "lien_quan": ["ND_155_2020", "LUAT_CK_2019"]
    },
    {
        "id": "TT_118_2020",
        "so_hieu": "118/2020/TT-BTC",
        "ten": "Thông tư 118/2020/TT-BTC hướng dẫn hoạt động giao dịch chứng khoán",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn một số nội dung về giao dịch chứng khoán trên hệ thống giao dịch của Sở giao dịch chứng khoán Việt Nam.

Điều 6. Giờ giao dịch
Thời gian giao dịch chứng khoán niêm yết tại Sở giao dịch: Phiên sáng từ 9h00 đến 11h30; Phiên chiều từ 13h00 đến 14h45; Giao dịch thỏa thuận đến 15h00.

Điều 10. Biên độ dao động giá
Biên độ dao động giá cổ phiếu niêm yết tại HOSE: +/- 7%; tại HNX: +/- 10%; tại UPCoM: +/- 15%.

Điều 15. Lệnh giao dịch
Các loại lệnh giao dịch bao gồm: Lệnh giới hạn (LO), Lệnh thị trường (MP, ATO, ATC), Lệnh điều kiện.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "TT_119_2020",
        "so_hieu": "119/2020/TT-BTC",
        "ten": "Thông tư 119/2020/TT-BTC hướng dẫn hoạt động đăng ký, lưu ký chứng khoán",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn hoạt động đăng ký, lưu ký, bù trừ và thanh toán giao dịch chứng khoán.

Điều 5. Đăng ký chứng khoán
Tổ chức phát hành phải thực hiện đăng ký chứng khoán tập trung tại Tổng công ty Lưu ký và Bù trừ chứng khoán Việt Nam (VSDC).

Điều 12. Thanh toán giao dịch
Thời gian thanh toán giao dịch chứng khoán là T+2 (02 ngày làm việc kể từ ngày giao dịch).

Điều 18. Quyền lợi cổ đông
Ngày đăng ký cuối cùng để thực hiện quyền là ngày T+1 kể từ ngày giao dịch không hưởng quyền.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "QD_22_2023",
        "so_hieu": "22/2023/QĐ-TTg",
        "ten": "Quyết định 22/2023/QĐ-TTg về thuế cổ tức",
        "loai": "Quyết định",
        "co_quan": "Thủ tướng Chính phủ",
        "ngay_ban_hanh": "2023-08-15",
        "ngay_hieu_luc": "2023-10-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Quyết định này quy định về chính sách thuế thu nhập cá nhân đối với cổ tức từ đầu tư chứng khoán.

Điều 3. Thuế suất cổ tức
Thuế suất thuế thu nhập cá nhân đối với thu nhập từ cổ tức bằng tiền là 5%.

Điều 5. Miễn thuế
Cổ tức bằng cổ phiếu không chịu thuế thu nhập cá nhân tại thời điểm nhận. Thuế chỉ phát sinh khi nhà đầu tư chuyển nhượng cổ phiếu đó.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "LUAT_DN_2020",
        "so_hieu": "59/2020/QH14",
        "ten": "Luật Doanh nghiệp 2020",
        "loai": "Luật",
        "co_quan": "Quốc hội",
        "ngay_ban_hanh": "2020-06-17",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Luật này quy định về việc thành lập, tổ chức quản lý, tổ chức lại, giải thể và hoạt động có liên quan của doanh nghiệp.

Điều 111. Công ty cổ phần
Công ty cổ phần là doanh nghiệp trong đó vốn điều lệ được chia thành nhiều phần bằng nhau gọi là cổ phần. Cổ đông có thể là tổ chức, cá nhân; số lượng cổ đông tối thiểu là 03.

Điều 120. Cổ phiếu
Cổ phiếu là chứng chỉ do công ty cổ phần phát hành, bút toán ghi sổ hoặc dữ liệu điện tử xác nhận quyền sở hữu cổ phần.

Điều 124. Phát hành cổ phần
Công ty cổ phần phát hành cổ phần để huy động vốn. Việc phát hành cổ phần phải tuân thủ quy định của Luật này và Luật Chứng khoán.""",
        "lien_quan": ["LUAT_CK_2019"]
    },
    {
        "id": "TT_96_2020",
        "so_hieu": "96/2020/TT-BTC",
        "ten": "Thông tư 96/2020/TT-BTC hướng dẫn công bố thông tin trên thị trường chứng khoán",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2020-11-16",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn về công bố thông tin trên thị trường chứng khoán.

Điều 7. Công bố thông tin định kỳ
Công ty đại chúng phải công bố: Báo cáo tài chính năm đã kiểm toán (trong vòng 90 ngày kể từ ngày kết thúc năm tài chính); Báo cáo tài chính bán niên (trong vòng 45 ngày).

Điều 10. Công bố thông tin bất thường
Trong vòng 24 giờ phải công bố khi: thay đổi thành viên HĐQT; thua lỗ bất thường; bị khởi kiện; thay đổi giấy phép kinh doanh.

Điều 15. Công bố thông tin về giao dịch cổ phiếu
Cổ đông lớn (sở hữu từ 5% trở lên) phải công bố trong vòng 3 ngày khi thay đổi tỷ lệ sở hữu.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "ND_156_2020",
        "so_hieu": "156/2020/NĐ-CP",
        "ten": "Nghị định 156/2020/NĐ-CP xử phạt vi phạm hành chính trong lĩnh vực chứng khoán",
        "loai": "Nghị định",
        "co_quan": "Chính phủ",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Nghị định này quy định về hành vi vi phạm hành chính, hình thức xử phạt, mức xử phạt, biện pháp khắc phục hậu quả trong lĩnh vực chứng khoán và thị trường chứng khoán.

Điều 5. Mức phạt tiền tối đa
Mức phạt tiền tối đa đối với tổ chức vi phạm là 3 tỷ đồng; đối với cá nhân vi phạm là 1,5 tỷ đồng.

Điều 14. Vi phạm về giao dịch nội bộ
Phạt tiền từ 3% đến 5% giá trị giao dịch vi phạm đối với hành vi sử dụng thông tin nội bộ để mua bán chứng khoán.

Điều 33. Vi phạm về thao túng thị trường
Phạt tiền từ 5% đến 10% giá trị giao dịch vi phạm đối với hành vi thao túng giá chứng khoán. Trường hợp nghiêm trọng có thể bị truy cứu trách nhiệm hình sự.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "TT_98_2020",
        "so_hieu": "98/2020/TT-BTC",
        "ten": "Thông tư 98/2020/TT-BTC hướng dẫn hoạt động và quản lý quỹ đầu tư chứng khoán",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2020-11-16",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn hoạt động và quản lý quỹ đầu tư chứng khoán, công ty đầu tư chứng khoán.

Điều 8. Quỹ mở
Quỹ mở là quỹ đầu tư chứng khoán mà chứng chỉ quỹ đã chào bán ra công chúng phải được mua lại theo yêu cầu của nhà đầu tư.

Điều 15. Giới hạn đầu tư
Quỹ đầu tư chứng khoán không được đầu tư quá 10% tổng giá trị tài sản vào chứng khoán của một tổ chức phát hành.

Điều 22. Báo cáo và công bố thông tin
Công ty quản lý quỹ phải báo cáo giá trị tài sản ròng (NAV) hàng ngày đối với quỹ mở và hàng tuần đối với quỹ đóng.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "TT_120_2020",
        "so_hieu": "120/2020/TT-BTC",
        "ten": "Thông tư 120/2020/TT-BTC hướng dẫn chế độ tài chính và giám sát hoạt động Sở giao dịch",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn chế độ tài chính và hoạt động giám sát đối với Sở giao dịch chứng khoán Việt Nam và Tổng công ty Lưu ký và Bù trừ chứng khoán Việt Nam.

Điều 5. Giám sát giao dịch
Sở giao dịch chứng khoán thực hiện giám sát giao dịch bất thường, phát hiện các hành vi thao túng giá, giao dịch nội gián.

Điều 10. Quỹ bù trừ
Thành viên bù trừ phải đóng góp vào quỹ bù trừ để bảo đảm thanh toán trong trường hợp thành viên mất khả năng thanh toán.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "LUAT_THUE_TNCN_2007",
        "so_hieu": "04/2007/QH12",
        "ten": "Luật Thuế thu nhập cá nhân 2007 (sửa đổi 2012, 2014)",
        "loai": "Luật",
        "co_quan": "Quốc hội",
        "ngay_ban_hanh": "2007-11-21",
        "ngay_hieu_luc": "2009-01-01",
        "tinh_trang": "Còn hiệu lực (sửa đổi)",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Luật này quy định về đối tượng nộp thuế, thu nhập chịu thuế, thu nhập được miễn thuế, giảm thuế và căn cứ tính thuế thu nhập cá nhân.

Điều 13. Thu nhập từ đầu tư vốn
Thu nhập từ đầu tư vốn bao gồm: cổ tức, lợi tức được chia. Thuế suất đối với thu nhập từ đầu tư vốn là 5%.

Điều 16. Thu nhập từ chuyển nhượng chứng khoán
Thu nhập từ chuyển nhượng chứng khoán chịu thuế suất 0,1% trên giá chuyển nhượng chứng khoán từng lần. Cá nhân có thể chọn nộp thuế 20% trên thu nhập ròng nếu kê khai đầy đủ chi phí.""",
        "lien_quan": ["LUAT_CK_2019", "QD_22_2023"]
    },
    {
        "id": "ND_158_2020",
        "so_hieu": "158/2020/NĐ-CP",
        "ten": "Nghị định 158/2020/NĐ-CP về chứng khoán phái sinh và thị trường chứng khoán phái sinh",
        "loai": "Nghị định",
        "co_quan": "Chính phủ",
        "ngay_ban_hanh": "2020-12-31",
        "ngay_hieu_luc": "2021-01-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Nghị định này quy định về chứng khoán phái sinh và thị trường chứng khoán phái sinh tại Việt Nam.

Điều 4. Các loại chứng khoán phái sinh
Chứng khoán phái sinh bao gồm: Hợp đồng tương lai chỉ số, Hợp đồng tương lai trái phiếu Chính phủ, Hợp đồng quyền chọn.

Điều 8. Điều kiện kinh doanh chứng khoán phái sinh
Công ty chứng khoán phải có vốn điều lệ tối thiểu 900 tỷ đồng và được Ủy ban Chứng khoán Nhà nước cấp giấy phép.

Điều 15. Ký quỹ giao dịch
Nhà đầu tư phải duy trì mức ký quỹ theo quy định. Mức ký quỹ ban đầu tối thiểu do Tổng công ty Lưu ký quy định.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "TT_58_2021",
        "so_hieu": "58/2021/TT-BTC",
        "ten": "Thông tư 58/2021/TT-BTC hướng dẫn phòng chống rửa tiền trong lĩnh vực chứng khoán",
        "loai": "Thông tư",
        "co_quan": "Bộ Tài chính",
        "ngay_ban_hanh": "2021-07-12",
        "ngay_hieu_luc": "2021-09-01",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Điều 1. Phạm vi điều chỉnh
Thông tư này hướng dẫn biện pháp phòng, chống rửa tiền trong lĩnh vực chứng khoán.

Điều 5. Nhận biết khách hàng (KYC)
Công ty chứng khoán phải thực hiện nhận biết khách hàng trước khi mở tài khoản giao dịch. Thông tin tối thiểu gồm: họ tên, ngày sinh, CCCD, địa chỉ, nghề nghiệp, mục đích giao dịch.

Điều 10. Báo cáo giao dịch đáng ngờ
Công ty chứng khoán phải báo cáo Cơ quan phòng chống rửa tiền khi phát hiện giao dịch đáng ngờ: giao dịch lớn bất thường, giao dịch không phù hợp với mục đích kinh doanh của khách hàng.

Điều 15. Lưu trữ hồ sơ
Hồ sơ nhận biết khách hàng và giao dịch phải được lưu trữ tối thiểu 5 năm kể từ ngày kết thúc giao dịch.""",
        "lien_quan": ["LUAT_CK_2019", "ND_155_2020"]
    },
    {
        "id": "CV_UBCK_2024",
        "so_hieu": "3456/UBCKNN-GSDC",
        "ten": "Công văn 3456/UBCKNN-GSDC về tăng cường giám sát giao dịch chứng khoán",
        "loai": "Công văn",
        "co_quan": "Ủy ban Chứng khoán Nhà nước",
        "ngay_ban_hanh": "2024-06-15",
        "ngay_hieu_luc": "2024-06-15",
        "tinh_trang": "Còn hiệu lực",
        "noi_dung": """Nội dung chính:
Ủy ban Chứng khoán Nhà nước yêu cầu các công ty chứng khoán tăng cường giám sát giao dịch, đặc biệt:

1. Giám sát chặt chẽ các tài khoản có giao dịch bất thường
2. Tăng cường kiểm soát giao dịch ký quỹ (margin)
3. Rà soát danh sách cổ phiếu được phép giao dịch ký quỹ
4. Báo cáo kịp thời các trường hợp nghi ngờ thao túng giá
5. Nâng cao chất lượng công bố thông tin cho nhà đầu tư""",
        "lien_quan": ["LUAT_CK_2019", "ND_156_2020", "TT_120_2020"]
    }
]

# Quan hệ giữa các văn bản cho Knowledge Graph
RELATIONS = [
    {"from": "ND_155_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "ND_128_2024", "to": "ND_155_2020", "type": "AMENDS", "label": "Sửa đổi"},
    {"from": "TT_118_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_118_2020", "to": "ND_155_2020", "type": "IMPLEMENTS", "label": "Chi tiết hóa"},
    {"from": "TT_119_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_119_2020", "to": "ND_155_2020", "type": "IMPLEMENTS", "label": "Chi tiết hóa"},
    {"from": "QD_22_2023", "to": "LUAT_CK_2019", "type": "IMPLEMENTS", "label": "Thực thi"},
    {"from": "QD_22_2023", "to": "ND_155_2020", "type": "REFERENCES", "label": "Tham chiếu"},
    {"from": "TT_96_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_96_2020", "to": "ND_155_2020", "type": "IMPLEMENTS", "label": "Chi tiết hóa"},
    {"from": "LUAT_DN_2020", "to": "LUAT_CK_2019", "type": "RELATED_TO", "label": "Liên quan"},
    {"from": "ND_128_2024", "to": "LUAT_CK_2019", "type": "REFERENCES", "label": "Tham chiếu"},
    {"from": "ND_156_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "ND_156_2020", "to": "ND_155_2020", "type": "RELATED_TO", "label": "Liên quan"},
    {"from": "TT_98_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_120_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "LUAT_THUE_TNCN_2007", "to": "QD_22_2023", "type": "RELATED_TO", "label": "Liên quan"},
    {"from": "LUAT_THUE_TNCN_2007", "to": "LUAT_CK_2019", "type": "RELATED_TO", "label": "Liên quan"},
    {"from": "ND_158_2020", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_58_2021", "to": "LUAT_CK_2019", "type": "GUIDES", "label": "Hướng dẫn"},
    {"from": "TT_58_2021", "to": "ND_155_2020", "type": "REFERENCES", "label": "Tham chiếu"},
    {"from": "CV_UBCK_2024", "to": "LUAT_CK_2019", "type": "REFERENCES", "label": "Tham chiếu"},
    {"from": "CV_UBCK_2024", "to": "ND_156_2020", "type": "REFERENCES", "label": "Tham chiếu"},
    {"from": "CV_UBCK_2024", "to": "TT_120_2020", "type": "REFERENCES", "label": "Tham chiếu"},
]

def generate_sample_data():
    """Tạo dữ liệu mẫu và lưu vào data/sample/"""
    os.makedirs("data/sample", exist_ok=True)
    with open("data/sample/documents.json", "w", encoding="utf-8") as f:
        json.dump(SAMPLE_DOCS, f, ensure_ascii=False, indent=2)
    with open("data/sample/relations.json", "w", encoding="utf-8") as f:
        json.dump(RELATIONS, f, ensure_ascii=False, indent=2)
    print(f"[+] Đã tạo {len(SAMPLE_DOCS)} văn bản mẫu và {len(RELATIONS)} quan hệ.")

if __name__ == "__main__":
    generate_sample_data()
