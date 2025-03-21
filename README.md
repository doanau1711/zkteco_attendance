📌 Hướng Dẫn Đồng Bộ Dữ Liệu Máy Chấm Công ZKTeco với Odoo 17

📝 Bước 1: Kết Nối Máy Chấm Công ZKTeco Với Odoo 17

📌 Yêu cầu: Máy chấm công ZKTeco và Odoo 17 phải cùng kết nối trong một mạng WiFi.

Đăng nhập vào máy chấm công ZKTeco.

Vào Thiết lập liên kết → Ethernet → Ghi nhớ Địa chỉ IP của máy chấm công (VD: 192.168.1.23). (B1.1)

Tiếp tục vào Cài đặt máy chủ đám mây → Địa chỉ máy chủ → Nhập địa chỉ IPv4 address của máy tính đang dùng.

Cách lấy IPv4: Vào WiFi trên laptop → Properties → Kéo xuống phần IPv4 address để lấy địa chỉ.

Cổng máy chủ: Chọn 8088.

📝 Bước 2: Kiểm Tra ID Người Dùng Trên Máy Chấm Công

📌 Yêu cầu: Cần có thông tin ID của người dùng trên máy chấm công để liên kết với Odoo.

Đăng nhập vào máy chấm công ZKTeco.

Vào Người sử dụng → Tất cả người sử dụng.

Tìm kiếm người dùng đã đăng ký, ID của người dùng là số hiển thị tương ứng.

📝 Bước 3: Kiểm Tra Múi Giờ

📌 Yêu cầu: Đảm bảo múi giờ của Windows, trình duyệt, và PostgreSQL trùng khớp.

Kiểm tra múi giờ trên Windows:

Vào Settings → Time & Language → Date & Time → Xem TimeZone.

VD: Asia/Bangkok.

Kiểm tra múi giờ trên trình duyệt (Chrome, Cốc Cốc, Firefox, v.v.):

Nhấn F12 hoặc Ctrl + Shift + I để mở DevTools.

Chuyển sang tab Console, nhập lệnh:

Intl.DateTimeFormat().resolvedOptions().timeZone;

VD: Asia/Bangkok.

Kiểm tra múi giờ trong PostgreSQL:

Mở PostgreSQL và chạy lệnh:

SHOW timezone;

Kết quả phải là UTC. Nếu không, chạy lệnh sau để đặt lại timezone:

ALTER DATABASE your_database SET timezone TO 'UTC';

📝 Bước 4: Cài Đặt Module "ZK-Biometric Device Integration" Trên Odoo 17

📌 Yêu cầu: Cài đặt module này sẽ tự động kích hoạt hai module quan trọng là Attendances và Employees.

1️⃣ Liên kết ID người dùng trong Odoo

Vào Module Employees → Employees.

Chọn một nhân viên bất kỳ (VD: Beth Evans).

Vào tab HR setting → Biometric Device ID → Nhập ID của người dùng trên máy chấm công.

2️⃣ Cấu hình thiết bị chấm công trong Odoo

Vào Module Attendances → Biometric Device → Device Configuration → New.

Nhập các thông tin cần thiết:

Name: Tên tùy chọn.

Device IP: Địa chỉ IP từ Bước 1 (192.168.1.23). (B1.1)

Data Range: Chọn ngày muốn lấy dữ liệu từ máy chấm công.

Port Number: 4370.

3️⃣ Kiểm tra và đồng bộ dữ liệu

Sau khi tạo mới, chọn thiết bị vừa thêm → Nhấn Test Connection.

Nếu kết nối thành công, sẽ có thông báo Connect Successfully.

Tiến hành chấm công trên máy chấm công ZKTeco.

Quay lại Odoo, nhấn Download Data để lấy dữ liệu từ máy chấm công về.

Xem dữ liệu tại Attendances Log.

📝 Bước 5: Các Thư Viện Yêu Cầu

📌 Yêu cầu: Cần cài đặt một số thư viện Python để hệ thống hoạt động ổn định
Chạy lệnh sau để cài đặt các thư viện cần thiết:
pip install pyzk


