# Dùng OpenCode CLI với LangGraph

Hướng dẫn này chạy OpenCode trực tiếp trong WSL/Linux thay vì trong container.
OpenCode có thể làm việc trong bất kỳ project nào, còn LangGraph vẫn chạy qua
Docker Compose trong thư mục `sample/`.

## 1. Khởi động LangGraph

Tạo và điền Anthropic credentials trong `.env` nếu chưa làm:

```bash
cd /mnt/d/Code/langgraph-openai-serve/sample
cp .env.example .env
```

Khởi động API:

```bash
docker compose up --build -d langgraph
```

Kiểm tra API và model coding agent:

```bash
curl http://localhost:8000/v1/models
```

Kết quả cần có model `simple-graph-external-tools`.

## 2. Cài OpenCode CLI

Trong WSL/Linux, chạy trình cài đặt chính thức:

```bash
curl -fsSL https://opencode.ai/v2/install | bash
```

Mở terminal mới hoặc nạp lại shell configuration, rồi kiểm tra:

```bash
source ~/.bashrc
opencode --version
```

## 3. Cấu hình provider LangGraph toàn cục

Tạo file `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lgos/simple-graph-external-tools",
  "small_model": "lgos/simple-graph-external-tools",
  "provider": {
    "lgos": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LangGraph OpenAI Serve",
      "options": {
        "baseURL": "http://localhost:8000/v1",
        "apiKey": "DUMMY"
      },
      "models": {
        "simple-graph-external-tools": {
          "name": "LangGraph coding agent",
          "limit": {
            "context": 200000,
            "output": 1024
          }
        }
      }
    }
  }
}
```

`DUMMY` chỉ phù hợp cho sample không bật xác thực ở LGOS. Khi deploy API có
xác thực, thay bằng API key của deployment đó.

## 4. Dùng với dự án bất kỳ

Chuyển tới thư mục dự án muốn làm việc và chạy OpenCode:

```bash
cd /mnt/d/Code/my-other-project
opencode
```

OpenCode đọc cấu hình global, gọi `simple-graph-external-tools` qua LangGraph,
và chạy các tool đọc/sửa file trong thư mục project hiện tại.

!!! warning

    OpenCode có thể thay đổi file của project hiện tại. Kiểm tra `git diff`
    trước khi commit.

## Khắc phục sự cố

### `opencode: command not found`

Mở terminal WSL mới. Nếu vẫn chưa có, kiểm tra binary được cài tại:

```bash
~/.opencode/bin/opencode --version
```

### Không kết nối được LangGraph

Đảm bảo service đang chạy và healthy:

```bash
cd /mnt/d/Code/langgraph-openai-serve/sample
docker compose ps langgraph
```

Nếu LangGraph dùng cổng khác, thay `8000` trong `baseURL` của cấu hình
OpenCode bằng giá trị `LANGGRAPH_PORT` trong `.env`.
