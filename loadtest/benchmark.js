// k6 壓測：虛擬使用者反覆提交 CPU benchmark 請求，觀察 API 承載能力。
import http from "k6/http";
import { sleep } from "k6";

// 匯出 k6 設定；vus=50 表示 50 個虛擬使用者，duration=2m 表示持續兩分鐘。
export const options = {
  vus: 50,
  duration: "2m",
};

// 每個虛擬使用者會反覆執行此預設函式。
export default function () {
  // 送出 HTTP POST；JSON.stringify 將物件轉成 JSON 字串，header 指定內容型別。
  http.post(
    "http://api.hpc.local/benchmark",
    JSON.stringify({
      benchmark: "cpu",
      simulate_failure: false,
    }),
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  // 每次迭代暫停 0.1 秒，控制使用者請求節奏。
  sleep(0.1);
}
