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

> *Điền:Students are expected to request a degree audit at least two regular terms before their planned graduation. The audit highlights any unmet academic requirements but does not guarantee enrollment in the necessary courses.*

**Scores:** Context Recall: ____0.4 | Context Precision: ____0.4 | Faithfulness: ____0.3|
Relevance: ____0.45 | Completeness: ___0.6_ | Overall: ____

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?

> *Câu trả lời:Students should request a degree audit two regular terms before the intended graduation term. The audit identifies missing academic requirements but does not reserve a course seat. The formal graduation application is due by the census date of the intended graduation term*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | câu trả lời thiếu chi tiết|
| Why 1 | Tại sao symptom xảy ra? | retriever không lấy được chunk chứa thông tin chính xác|
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Query formulation chưa tốt|
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Chưa có cơ chế fallback khi evidence thiếu|
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Evaluation chỉ dựa vào score, chưa cross-check với evidence. |
| Why 5 | Root cause có thể hành động được là gì? | Cần cải thiện retriever (top-k, query expansion) hoặc thêm reranker để lọc nhiễu.|

**Root cause từ `find_root_cause()`:**

> *Paste output: Root cause: Root cause error*

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
| 1 |Misconfigured API key |F210 | Medium |
| 2 |Insufficient memory allocation | F310 | Medium|
| 3 | | | |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:Misconfigured API key, cluster này có vẻ dễ xử lý hơn*

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
[paste Markdown table here]
{'Date': '2026-08-13', 'Cluster': 1, 'Root Cause': 'Database connection timeout', 'Failure IDs': 'F123, F127', 'Priority': 'High', 'Improvement Action': 'Tối ưu connection pool, tăng timeout', 'Owner': 'Team A', 'Status': 'Planned'}
{'Date': '2026-08-13', 'Cluster': 2, 'Root Cause': 'Misconfigured API key', 'Failure IDs': 'F210, F211', 'Priority': 'Medium', 'Improvement Action': 'Cập nhật cấu hình key, thêm validation', 'Owner': 'Team B', 'Status': 'Planned'}
{'Date': '2026-08-13', 'Cluster': 3, 'Root Cause': 'Insufficient memory allocation', 'Failure IDs': 'F305, F309', 'Priority': 'Low', 'Improvement Action': 'Nâng cấp RAM, tối ưu memory allocation', 'Owner': 'Team C', 'Status': 'Planned'}

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

> *Câu trả lời: sau khi có thay đổi code quan trọng*

**Câu 2: Threshold drop 0.05 có phù hợp Student Services không? Vì sao?**

> *Câu trả lời: Phù hợp nếu bạn muốn tránh cảnh báo giả và chỉ quan tâm đến thay đổi đáng kể. Nếu Student Services ưu tiên ổn định trải nghiệm, thì threshold nên nhỏ hơn 0.05 để phát hiện sớm vấn đề.*

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời: nếu lỗi ảnh hưởng trực tiếp đến trải nghiệm hoặc dữ liệu của người dùng thì block. Nếu lỗi nghiêm trọng hoặc xảy ra thường xuyên thì block; nếu nhẹ hoặc hiếm gặp thì alert.*

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [Unit/Integration Tests] → [Regression Tests] → [Evaluation/Approval Stage] → Deploy

```

> *Giải thích:
Unit/Integration Tests: kiểm tra các thành phần nhỏ và sự tương tác giữa chúng, đảm bảo thay đổi không phá vỡ logic cơ bản.

Regression Tests: chạy lại toàn bộ bộ test quan trọng để chắc chắn các chức năng cũ vẫn hoạt động sau thay đổi.

Evaluation/Approval Stage: đánh giá kết quả test, phân tích metric/failure, quyết định block hay chỉ alert. Đây là bước “gate” trước khi cho phép deploy. *

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 |Optimize memory allocation | Response time, error rate) |Hệ thống ổn định hơn, ít crash|
| 2 |Correct misconfigured API key |Authentication success rate | Giảm lỗi đăng nhập, cải thiện trải nghiệm|
| 3 | | | |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:
Misconfigured API key – ảnh hưởng trực tiếp đến authentication và user access.

(Tùy chọn) Insufficient memory allocation – tuy mức độ ưu tiên thấp hơn, nhưng vẫn cần theo dõi để tránh crash bất ngờ.*

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:*

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời: Dễ bias theo reference. Không đánh giá tính chính xác ngữ nghĩa*
