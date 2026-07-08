import http from "k6/http";
import { sleep } from "k6";

export const options = {
  vus: 50,
  duration: "2m",
};

export default function () {
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

  sleep(0.1);
}
