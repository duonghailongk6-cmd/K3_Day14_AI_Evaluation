# Day 14 — Reflection

## Evaluation Report & Failure Analysis

Dùng kết quả thật trong `artifacts/benchmark_results.json` và kiểm tra lại
answer/context trace trong `artifacts/actual_answers.json` trước khi kết luận.

---

## 1. Benchmark Results Summary

**Overall pass rate:** ____%

| Metric | Average | Min | Max | Nhận xét |
|---|---:|---:|---:|---|
| Context Recall | ≥ 0.8|≥ 0.7 | ≤ 1.0| Nếu recall thấp, hệ thống dễ bỏ sót thông tin quan trọng từ ngữ cảnh trước → ảnh hưởng đến tính liền mạch. |
| Context Precision |≥ 0.85 | ≥ 0.75| ≤ 1.0| Precision thấp nghĩa là mô hình lấy nhầm thông tin từ ngữ cảnh → gây sai lệch. Đây là lỗi nghiêm trọng hơn recall.|
| Faithfulness | ≥ 0.9| ≥ 0.85 |≤ 1.0 | Sai sự thật là rủi ro lớn nhất, nên threshold phải cao. Đây là metric “hard block”.|
| Relevance |≥ 0.85 | ≥ 0.8| ≤ 1.0| Nếu câu trả lời không liên quan, trải nghiệm người dùng giảm mạnh.|
| Completeness | ≥ 0.8|≥ 0.7 |≤ 1.0 | Có thể chấp nhận thiếu chi tiết nhỏ, nhưng nếu completeness quá thấp thì câu trả lời không hữu ích.|
| Overall Score | ≥ 0.85| ≥ 0.8|≤ 1.0 |Điểm tổng hợp phải cao để đảm bảo chất lượng ổn định trước khi deployment. |

**Score interpretation**

- Metrics/cases ở mức Good (0.8–1.0): ____hoạt động ổn định, đáp ứng yêu cầu chất lượng
- Metrics/cases ở mức Needs Work (0.6–0.8): ____tạm ổn, cần cải thiện
- Metrics/cases ở mức Significant Issues (<0.6): ____không đạt yêu cầu

**Failure type distribution**

| Failure Type | Count | Percentage |
|---|---:|---:|
| hallucination |6 | 30%|Lỗi nghiêm trọng nhất vì mô hình bịa đặt hoặc cung cấp thông tin sai sự thật
| irrelevant | 4| 20%| Câu trả lời không liên quan đến câu hỏi
| incomplete | 5|25% | Câu trả lời thiếu chi tiết quan trọng
| off_topic |3 |15% | Câu trả lời đi lệch hoàn toàn khỏi chủ đề
| refusal | 2|10% | Mô hình từ chối trả lời ngay cả khi câu hỏi hợp lệ

**Chẩn đoán tổng quan:** Vấn đề chính nằm ở retrieval, generation hay cả hai?
Dùng ít nhất hai metrics để bảo vệ kết luận.

> *Vấn đề chủ yếu ở generation, dùng bertscore để đánh giá dữ liệu được sinh ra, Faithfulness và Relevance  đánh giá kết quả truy vấn*

---

## 2. Top 3 Worst Failures — 5 Whys

Phân loại failure trước khi đề xuất fix. Với mỗi case, kiểm tra cả gold evidence
và retrieved chunks; không suy luận chỉ từ một score.

### Failure 1

**ID và question:**

> *Điền:H02 How does a graduation audit interact with updated policies effective August 1, 2026?*

**Expected answer:**

> *Điền:A graduation audit will consider the updated policies effective August 1, 2026, and students must ensure they meet the new requirements to be eligible for graduation.*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | câu trả lời thiếu chi tiết|
| Why 1 | Tại sao symptom xảy ra? | retriever không lấy được chunk chứa thông tin chính xác|
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Query formulation chưa tốt|
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Chưa có cơ chế fallback khi evidence thiếu|
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Evaluation chỉ dựa vào score, chưa cross-check với evidence. |
| Why 5 | Root cause có thể hành động được là gì? | Cần cải thiện retriever (top-k, query expansion) hoặc thêm reranker để lọc nhiễu.|

**Root cause từ `find_root_cause()`:**

> *Paste output:*

**Bạn đồng ý hay không? Dẫn evidence từ trace:**

> *Câu trả lời:*

**Proposed fix cụ thể:**

> *Câu trả lời:*

### Failure 2

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:**

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause và proposed fix:**

> *Câu trả lời:*



## 3. Failure Clustering

Một root cause có thể tạo ra nhiều failures. Nhóm theo nguyên nhân có thể sửa,
không chỉ nhóm theo tên metric.

| Cluster | Root Cause | Failure IDs | Priority |
|---|---|---|---|
| 1 | | | High/Medium/Low |
| 2 | | | |
| 3 | | | |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:*

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
[paste Markdown table here]
```

**Ba improvement suggestions ưu tiên**

1. ____
2. ____
3. ____

Với mỗi suggestion, nêu metric dự kiến thay đổi và cách đo lại.

| Suggestion | Target metric | Verification method |
|---|---|---|
| | | |
| | | |
| | | |

---

## 5. Regression Testing Strategy

**Câu 1: Khi nào chạy `run_regression()` trong production workflow?**

> *Câu trả lời:*

**Câu 2: Threshold drop 0.05 có phù hợp Student Services không? Vì sao?**

> *Câu trả lời:*

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời:*

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [________] → [________] → [________] → Deploy
```

> *Giải thích:*

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:*

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:*

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời:*
