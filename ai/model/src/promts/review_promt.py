system_review_promt = """Bạn là một chuyên gia du lịch giàu kinh nghiệm, chuyên cung cấp những mẹo du lịch thực tế và hữu ích cho khách du lịch.

Khi được yêu cầu tìm kiếm thông tin du lịch, bạn cần:
1. Tìm kiếm thông tin từ nhiều nguồn đáng tin cậy
2. Tập trung vào thông tin thực tế, có thể áp dụng ngay
3. Ưu tiên thông tin từ người dân địa phương và du khách có kinh nghiệm
4. Cung cấp thông tin chi tiết về:
   - Thời gian tốt nhất để tham quan
   - Cách di chuyển và phương tiện
   - Chi phí dự kiến
   - Những điều cần tránh
   - Mẹo tiết kiệm
   - Văn hóa và phong tục địa phương

Hãy trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu. Mỗi mẹo nên có 1-2 câu giải thích ngắn gọn."""

few_shot_review_promt = """
        ### Ngày 1: Khám phá phố cổ Hà Nội

        1. **Thời điểm lý tưởng**: Nếu muốn tận hưởng vẻ đẹp bình yên của Hà Nội, bạn hãy dậy sớm từ 6:00 - 8:00. Lúc này, phố phường còn tĩnh lặng, bạn có thể ngắm nhìn nhịp sống buổi sáng của người dân mà không phải lo lắng về đông đúc.
        2. **Di chuyển**: Để có thể khám phá từng ngóc ngách của phố cổ, hãy chọn đi bộ hoặc thuê xe đạp. Những con phố nhỏ sẽ trở nên thú vị hơn khi bạn tự mình lang thang khám phá.
        3. **Chi phí ước tính**: Khoảng 500,000 VND cho cả ngày, đủ để bạn thưởng thức món ngon và tham gia vào các hoạt động mua sắm.
        4. **Mẹo mua sắm**: Hãy tránh mua đồ ở các cửa hàng đầu phố vì giá cả thường cao hơn so với những cửa hàng nhỏ trong các ngõ.
        5. **Tiết kiệm chi phí**: Nếu muốn trải nghiệm ăn sáng với giá hợp lý, đừng ngần ngại dừng chân ở một quán vỉa hè. Mỗi phần ăn chỉ khoảng 20,000 - 30,000 VND nhưng lại rất ngon.
        6. **Văn hóa cần lưu ý**: Khi vào chùa, nhớ mặc đồ kín đáo và cởi giày trước khi bước vào. Đây là nét đẹp văn hóa đáng trân trọng.

        ### Ngày 2: Thưởng thức ẩm thực Hà Nội

        1. **Thời gian lý tưởng**: Hãy dành buổi tối từ 18:00 - 21:00 để thưởng thức những món ăn đặc sắc của Hà Nội. Lúc này, các quán ăn sôi động hơn và bạn sẽ cảm nhận được không khí ẩm thực đường phố thật sự.
        2. **Di chuyển**: Bạn chỉ cần đi bộ giữa các quán ăn, vì khoảng cách giữa chúng rất gần nhau. Đây là cơ hội tuyệt vời để vừa thưởng thức đồ ăn, vừa ngắm nhìn phố xá về đêm.
        3. **Chi phí ước tính**: Một buổi tối thưởng thức ẩm thực có thể dao động từ 300,000 - 400,000 VND, đủ để bạn nếm thử nhiều món ngon và thưởng thức các món uống đặc trưng.
        4. **Mẹo ăn uống**: Đừng ăn quá no ở một quán, hãy thử món ở nhiều quán khác nhau để khám phá được hết hương vị đa dạng của Hà Nội.
        5. **Tiết kiệm chi phí**: Nếu đi cùng bạn bè, hãy chia sẻ món ăn. Bạn sẽ có cơ hội thử nhiều món mà không phải lo lắng về chi phí.
        6. **Văn hóa cần lưu ý**: Khi ăn phở, đừng quên thêm rau thơm và nước mắm theo khẩu vị của mình để món ăn thêm phần đậm đà.
"""

reviewer_promt = """
Hãy cung cấp 5-6 mẹo du lịch thực tế CHO RIÊNG NGÀY NÀY, bao gồm:
            1. Thời gian tốt nhất để tham quan các địa điểm
            2. Cách di chuyển giữa các địa điểm
            3. Chi phí dự kiến cho cả ngày
            4. Những điều cần tránh
            5. Mẹo tiết kiệm
            6. Văn hóa và phong tục địa phương cần lưu ý
            Các hoạt động trong ngày này:
            """
note_promt = """
Lưu ý:
            - Hãy cung cấp thông tin thực tế, có thể áp dụng ngay
            - Ưu tiên thông tin từ người dân địa phương và du khách có kinh nghiệm
            - Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu
            - Mỗi tip nên có 1-2 câu giải thích ngắn gọn
            - CHỈ CUNG CẤP TIPS CHO NGÀY ĐANG ĐƯỢC XEM XÉT, KHÔNG BAO GỒM CÁC NGÀY KHÁC
            - Format tips giống như ví dụ trên
            - Mỗi ngày chỉ nên có 5-6 mẹo du lịch thực tế
            """

summary_tips_promt = """
        Yêu cầu:
        1. Chuyển đổi thành danh sách các tips đơn giản, mỗi tip là một câu
        2. Loại bỏ các tiêu đề, định dạng phức tạp, số thứ tự
        3. Giữ lại nội dung chính của mỗi tip
        4. Viết ngắn gọn, súc tích và hữu ích
        5. Giữ nguyên tiếng Việt
        6. Trả về CHÍNH XÁC danh sách các tips, mỗi tip trên một dòng
        7. Nếu tips đó cụ thể cho địa điểm đó thì cứ viết tên địa điểm đó vào tips

        Ví dụ: 
        Input:
        "1. **Thời điểm lý tưởng**: Nên bắt đầu sớm để tránh cái nóng và đông đúc."

        Output:
        "Nên bắt đầu sớm từ 6-8h sáng để tránh nóng và đông đúc."
"""
