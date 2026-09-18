# Hướng dẫn cài đặt sample

Sample này chạy LangGraph OpenAI Serve (LGOS) qua Docker Compose. Bạn có thể
dùng Open WebUI để chat hoặc OpenCode làm coding agent. Cả hai đều kết nối tới
LangGraph qua OpenAI-compatible API tại `/v1`.

## Yêu cầu

- Docker Engine 24+ và Docker Compose plugin (`docker compose version`)
- Anthropic API key và workspace ID có quyền dùng model đã chọn
- Cổng `8000` và `3000` còn trống trên máy host (hoặc đổi trong `.env`)

## Cấu hình

Từ thư mục `sample/`, tạo file môi trường cục bộ:

```bash
cp .env.example .env
```

Mở `.env` và cập nhật tối thiểu hai giá trị sau:

```dotenv
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_WORKSPACE_ID=your-anthropic-workspace-id
```

Tùy chọn, chọn model Anthropic khác hoặc đổi cổng host:

```dotenv
ANTHROPIC_MODEL=claude-haiku-4-5
LANGGRAPH_PORT=8000
OPEN_WEBUI_PORT=3000
```

`ANTHROPIC_BASE_URL` chỉ cần đổi khi bạn sử dụng một Anthropic-compatible
proxy.

## Chạy LangGraph và Open WebUI

Build image rồi khởi động toàn bộ sample:

```bash
docker compose up --build
```

Mở [http://localhost:3000](http://localhost:3000), chọn model `simple-graph`,
rồi bắt đầu chat.

Để chỉ chạy API LangGraph:

```bash
docker compose up --build -d langgraph
```

Xem những model đã đăng ký:

```bash
curl http://localhost:8000/v1/models
```

Kết quả cần có `simple-graph` và `simple-graph-external-tools`.

## Chạy OpenCode

OpenCode là một profile tùy chọn, không tự chạy khi gọi `docker compose up`.
Sau khi LangGraph đã healthy, mở phiên OpenCode tương tác:

```bash
docker compose run --rm opencode
```

Nó dùng model `lgos/simple-graph-external-tools`. Model này trả về các OpenAI
function calls; OpenCode thực thi tool đọc, sửa file và chạy lệnh trong thư mục
repository được mount vào container tại `/workspace`.

!!! warning

    Agent có thể thay đổi các file trong repository của bạn. Kiểm tra thay đổi
    bằng `git diff` trước khi commit.

Đổi phiên bản image OpenCode bằng `OPENCODE_IMAGE` trong `.env`, sau đó chạy
lại lệnh `docker compose run --rm opencode`.

## Khắc phục sự cố

### `ModuleNotFoundError: No module named 'external_tools'`

Image LangGraph đang được build từ phiên bản cũ. Build lại và tạo lại service:

```bash
docker compose up --build -d --force-recreate langgraph
```

### `store` hoặc `prompt_cache_key: Extra inputs are not permitted`

OpenCode gửi các tuỳ chọn cache/storage này trong request Chat Completions,
trong khi bản LGOS được ghim trong sample chưa nhận diện chúng. Sample đã bỏ
qua các tuỳ chọn này vì không có response storage hoặc cache namespace; build
lại image để áp dụng middleware:

```bash
docker compose up --build -d --force-recreate langgraph
```

### Service không healthy

Xem log:

```bash
docker compose logs -f langgraph
```

Kiểm tra `ANTHROPIC_API_KEY`, `ANTHROPIC_WORKSPACE_ID` và model trong `.env`.
Endpoint health không gọi Anthropic, nên lỗi credentials thường chỉ hiện khi
gửi chat hoặc chạy OpenCode.

### Cổng đã được sử dụng

Đổi `LANGGRAPH_PORT` hoặc `OPEN_WEBUI_PORT` trong `.env`, ví dụ:

```dotenv
LANGGRAPH_PORT=8010
OPEN_WEBUI_PORT=3010
```

## Dừng và dọn dẹp

```bash
docker compose down
```

Muốn xóa cả dữ liệu Open WebUI (tài khoản và lịch sử chat), dùng:

```bash
docker compose down --volumes
```
