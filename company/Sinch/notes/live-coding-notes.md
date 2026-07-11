# Live Coding Notes

Live coding 的核心不是写得多快，而是让面试官看见你在有条理地解决问题。它更像协作调试，而不是闭卷考试。

## 现场节奏

1. 先复述题意：确认输入、输出、边界条件、约束。
2. 说出方案：先讲最直接可行的思路，再提复杂度。
3. 边写边解释：不要沉默太久，让面试官知道你在想什么。
4. 写完先跑简单例子：用 happy path 验证。
5. 再补边界情况：空输入、重复值、null/None、极大值、异常输入。
6. 最后总结复杂度和可改进点。

## 特别要避免

- 一上来就写代码，没确认需求。
- 卡住后一直沉默。
- 为了“高级”过度抽象。
- 忘记处理边界条件。
- 代码跑不通但不解释排查思路。
- 面试官提示时只是点头，不把提示转化成下一步动作。

## 可以直接使用的表达

```text
Let me first clarify the expected input and output.
I’ll start with a straightforward solution, then we can optimize if needed.
I’m going to test this with a small example before moving on.
This handles the common case; now I want to check edge cases.
The time complexity is O(n), and the extra space is O(...).
```

## AI Engineer / Agent / RAG 相关重点

如果是 AI Engineer、Agent、RAG 相关 live coding，不只要写功能，还要讲清楚 trade-off。

常见关注点包括：

- chunking
- retrieval
- reranking
- prompt construction
- tool calling
- fallback
- evaluation
- latency
- cost
- observability
- failure mode
- guardrails

## 可以主动展示的 production 意识

```text
For a production version, I’d add logging around retrieval quality and model failures.
I’d separate orchestration logic from model/provider-specific code.
I’d write tests for deterministic parts and mock the LLM call.
```

## 一句话总结

先沟通，再编码；边解释，边验证；写完别急着结束，要主动讲测试、复杂度和 production trade-off。
