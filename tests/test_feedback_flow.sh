#!/bin/bash

# 测试反馈功能的脚本

API_BASE="http://localhost:8000"

echo "========================================="
echo "测试智能体反馈功能"
echo "========================================="
echo ""

# 1. 发送初始请求
echo "1️⃣ 发送初始请求..."
echo ""

RESPONSE=$(curl -s -N "${API_BASE}/api/team-chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "生成一个简单的登录功能测试用例"
  }' \
  --no-buffer)

# 提取 conversation_id
CONVERSATION_ID=$(echo "$RESPONSE" | grep -o 'X-Conversation-ID: [^"]*' | head -1 | cut -d' ' -f2)

echo "📝 Conversation ID: $CONVERSATION_ID"
echo ""
echo "响应片段:"
echo "$RESPONSE" | head -20
echo "..."
echo ""

# 检查是否收到 feedback_request
if echo "$RESPONSE" | grep -q "feedback_request"; then
  echo "✅ 收到反馈请求"
  echo ""
else
  echo "❌ 未收到反馈请求"
  exit 1
fi

# 2. 发送反馈
echo "2️⃣ 发送用户反馈..."
echo ""

FEEDBACK_RESPONSE=$(curl -s -N "${API_BASE}/api/team-chat/stream" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"@TestCase_Generator 请添加边界测试用例\",
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"is_feedback\": true
  }" \
  --no-buffer)

echo "响应片段:"
echo "$FEEDBACK_RESPONSE" | head -20
echo "..."
echo ""

# 3. 发送"同意"结束对话
echo "3️⃣ 发送'同意'结束对话..."
echo ""

APPROVE_RESPONSE=$(curl -s -N "${API_BASE}/api/team-chat/stream" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"同意\",
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"is_feedback\": true
  }" \
  --no-buffer)

echo "响应:"
echo "$APPROVE_RESPONSE"
echo ""

if echo "$APPROVE_RESPONSE" | grep -q "用户已同意"; then
  echo "✅ 对话成功结束"
else
  echo "⚠️ 对话结束响应异常"
fi

echo ""
echo "========================================="
echo "测试完成"
echo "========================================="

