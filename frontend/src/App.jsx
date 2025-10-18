import React, { useState, useRef, useEffect } from 'react';
import { ConfigProvider, theme, App as AntApp, FloatButton, Badge, message } from 'antd';
import {
  RobotOutlined,
  SendOutlined,
  ClearOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  CodeOutlined,
  FileTextOutlined,
  SunOutlined,
  MoonOutlined,
  FireOutlined,
  RocketOutlined,
  HeartOutlined,
  StarOutlined,
  ExperimentOutlined,
  TeamOutlined,
  HomeOutlined,
  PaperClipOutlined,
  CopyOutlined,
  SaveOutlined,
  EditOutlined,
  RedoOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { Sender, useXAgent, useXChat } from '@ant-design/x';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import MatrixRain from './components/MatrixRain';
import ModeSelector from './components/ModeSelector';
import FileUpload from './components/FileUpload';
import ImageAnalyzer from './components/ImageAnalyzer';
import './App.css';

// API 配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 普通模式建议提示卡片
const SUGGESTIONS = [
  {
    icon: <ThunderboltOutlined />,
    text: '解释量子计算原理',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    emoji: '⚡'
  },
  {
    icon: <BulbOutlined />,
    text: '给我一些创意写作灵感',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    emoji: '💡'
  },
  {
    icon: <CodeOutlined />,
    text: '编写一个 Python 排序算法',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    emoji: '💻'
  },
];

// 编排模式建议提示卡片
const ORCHESTRATION_SUGGESTIONS = [
  {
    icon: <RobotOutlined />,
    text: '解释 AutoGen 智能体编排原理',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    emoji: '🤖'
  },
  {
    icon: <ThunderboltOutlined />,
    text: '演示智能体协作处理复杂任务',
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    emoji: '⚡'
  },
  {
    icon: <CodeOutlined />,
    text: '生成一个完整的 Python 项目结构',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    emoji: '💻'
  },
];

// 测试用例模式建议提示卡片
const TESTCASE_SUGGESTIONS = [
  {
    icon: <ExperimentOutlined />,
    text: '为用户登录功能生成测试用例',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    emoji: '🔐'
  },
  {
    icon: <FileTextOutlined />,
    text: '为购物车添加商品功能生成测试用例',
    gradient: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    emoji: '🛒'
  },
  {
    icon: <CodeOutlined />,
    text: '为支付接口生成测试用例',
    gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    emoji: '💳'
  },
];

function App() {
  // 为每种模式维护独立的消息列表
  const [normalMessages, setNormalMessages] = useState([]); // 普通对话模式的消息
  const [orchestrationMessages, setOrchestrationMessages] = useState([]); // 编排模式的消息
  const [testcaseMessages, setTestcaseMessages] = useState([]); // 智能体模式的消息
  const [loading, setLoading] = useState(false);
  const [isDark, setIsDark] = useState(true); // 默认深色主题
  const [inputValue, setInputValue] = useState('');
  const [selectedMode, setSelectedMode] = useState(null); // 'normal'、'orchestration' 或 'testcase'，null 表示未选择
  const [collapsedAgents, setCollapsedAgents] = useState({}); // 管理智能体折叠状态 {messageId: {agentName: boolean}}
  const [isStreaming, setIsStreaming] = useState(false); // 是否正在流式传输
  const [uploadedFiles, setUploadedFiles] = useState([]); // 上传的文件列表
  const [parsedFiles, setParsedFiles] = useState([]); // 已解析的文件列表
  const [isParsing, setIsParsing] = useState(false); // 是否正在解析文件
  const [autoScroll, setAutoScroll] = useState(true); // 是否自动滚动
  const [editingMessageId, setEditingMessageId] = useState(null); // 正在编辑的消息 ID
  const [editingContent, setEditingContent] = useState(''); // 编辑中的内容

  // 为每种模式维护独立的会话 ID
  const [normalConversationId, setNormalConversationId] = useState(null);
  const [orchestrationConversationId, setOrchestrationConversationId] = useState(null);
  const [testcaseConversationId, setTestcaseConversationId] = useState(null);

  const abortControllerRef = useRef(null); // 用于中止流式传输
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const lastScrollTopRef = useRef(0); // 记录上次滚动位置
  const isUserScrollingRef = useRef(false); // 标记用户是否正在滚动

  // 使用 useRef 存储会话ID，确保立即更新和访问
  const orchestrationSessionRef = useRef(null);
  const normalSessionRef = useRef(null);
  const testcaseSessionRef = useRef(null);

  // 根据当前模式获取对应的消息列表
  const messages = selectedMode === 'testcase' ? testcaseMessages :
                   selectedMode === 'orchestration' ? orchestrationMessages : normalMessages;
  const setMessages = selectedMode === 'testcase' ? setTestcaseMessages :
                      selectedMode === 'orchestration' ? setOrchestrationMessages : setNormalMessages;

  // 消息变化时滚动到底部（仅当自动滚动开启时）
  useEffect(() => {
    if (autoScroll && messagesEndRef.current && !isUserScrollingRef.current) {
      // 使用 setTimeout 确保 DOM 已更新
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [testcaseMessages, orchestrationMessages, normalMessages, autoScroll]); // 使用实际的状态而不是计算值

  // 监控编排模式会话ID的变化
  useEffect(() => {
    if (selectedMode === 'orchestration') {
      console.log('🔄 编排模式会话ID状态变化:', orchestrationConversationId);
    }
  }, [orchestrationConversationId, selectedMode]);

  // 监听用户滚动事件
  const handleScroll = (e) => {
    const container = e.target;
    const currentScrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    const isAtBottom = scrollHeight - currentScrollTop - clientHeight < 50;

    // 检测用户是否主动向上滚动
    const isScrollingUp = currentScrollTop < lastScrollTopRef.current;

    // 标记用户正在滚动
    isUserScrollingRef.current = true;

    // 如果用户主动向上滚动且不在底部，禁用自动滚动
    if (isScrollingUp && !isAtBottom) {
      if (autoScroll) {
        console.log('用户向上滚动，禁用自动滚动');
        setAutoScroll(false);
      }
    }
    // 如果用户滚动到底部，重新启用自动滚动
    else if (isAtBottom) {
      if (!autoScroll) {
        console.log('用户滚动到底部，启用自动滚动');
        setAutoScroll(true);
      }
    }

    lastScrollTopRef.current = currentScrollTop;

    // 延迟重置滚动标记
    setTimeout(() => {
      isUserScrollingRef.current = false;
    }, 150);
  };

  // 解析目标智能体（从 @ 提及中）
  const parseTargetAgent = (message) => {
    const match = message.match(/@(TestCase_\w+)/);
    return match ? match[1] : null;
  };

  // 处理"同意"按钮点击
  const handleApprove = async (messageId) => {
    const message = messages.find(msg => msg.id === messageId);
    if (!message || !message.feedbackRequest) return;

    // 保存会话 ID 和反馈信息
    const conversationId = message.conversationId;

    console.log('🟢 用户点击同意');
    console.log('🟢 消息对象:', message);
    console.log('🟢 会话 ID:', conversationId);
    console.log('🟢 feedbackRequest:', message.feedbackRequest);

    // 发送"同意"消息，传递会话信息
    await handleStreamingChat('同意', {
      isFeedback: true,
      conversationId: conversationId,
      targetAgent: null
    });
  };

  // 处理 SSE 流式传输（支持手动传递反馈信息）
  const handleStreamingChat = async (userMessage, manualFeedback = null) => {
    if (!userMessage.trim()) return;

    setLoading(true);
    setIsStreaming(true);
    setInputValue('');

    // 创建新的 AbortController
    abortControllerRef.current = new AbortController();

    // 获取成功解析的文件 ID
    const fileIds = parsedFiles
      .filter(f => f.success && f.file_id)
      .map(f => f.file_id);

    // 检查是否有待反馈的消息（优先使用手动传递的反馈信息）
    let isFeedback, conversationId, targetAgent;

    if (manualFeedback) {
      // 使用手动传递的反馈信息（来自"同意"按钮）
      isFeedback = manualFeedback.isFeedback;
      conversationId = manualFeedback.conversationId;
      targetAgent = manualFeedback.targetAgent;
      console.log('🔵 使用手动反馈信息:', { isFeedback, conversationId, targetAgent });
    } else {
      // 自动检测反馈消息
      const pendingFeedbackMessage = messages.find(msg => msg.feedbackRequest);
      isFeedback = !!pendingFeedbackMessage;
      conversationId = pendingFeedbackMessage?.conversationId;
      targetAgent = isFeedback ? parseTargetAgent(userMessage) : null;
      console.log('🔵 自动检测反馈信息:', { isFeedback, conversationId, targetAgent });
    }

    // 如果不是反馈消息，使用当前模式的会话 ID
    if (!isFeedback) {
      // 优先使用 ref 中的值，确保获取最新的会话ID
      if (selectedMode === 'testcase') {
        conversationId = testcaseSessionRef.current || testcaseConversationId;
      } else if (selectedMode === 'orchestration') {
        conversationId = orchestrationSessionRef.current || orchestrationConversationId;

        // 如果仍然没有会话ID，尝试从最近的消息中获取
        if (!conversationId) {
          const lastMessage = messages
            .slice()
            .reverse()
            .find(msg => msg.role === 'assistant' && msg.sessionId);
          if (lastMessage) {
            conversationId = lastMessage.sessionId;
            console.log('🔄 从消息历史中获取会话ID:', conversationId);
          }
        }
      } else {
        conversationId = normalSessionRef.current || normalConversationId;
      }

      console.log('🔵 使用当前模式的会话 ID:', conversationId);
      console.log('🔍 当前模式:', selectedMode);
      console.log('🔍 所有会话ID状态 (state):', {
        normal: normalConversationId,
        orchestration: orchestrationConversationId,
        testcase: testcaseConversationId
      });
      console.log('🔍 所有会话ID状态 (ref):', {
        normal: normalSessionRef.current,
        orchestration: orchestrationSessionRef.current,
        testcase: testcaseSessionRef.current
      });

      // 如果仍然没有会话ID，记录警告
      if (!conversationId && messages.length > 0) {
        console.warn('⚠️ 警告：应该有会话ID但未找到，这可能导致会话不连续');
      }
    }

    // 如果是反馈消息，清除之前消息的 feedbackRequest 标记
    if (isFeedback) {
      setMessages(prev =>
        prev.map(msg =>
          msg.feedbackRequest ? { ...msg, feedbackRequest: undefined } : msg
        )
      );
    }

    // 添加用户消息（显示原始问题）
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
      tokens: null, // 将在收到 token 信息后更新
      hasFiles: fileIds.length > 0, // 标记是否包含文件
      fileCount: fileIds.length, // 文件数量
    };

    setMessages(prev => [...prev, userMsg]);

    // 创建助手消息占位符
    const assistantMsgId = Date.now() + 1;
    const assistantMsg = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      streaming: true,
      tokens: null, // 将在收到 token 信息后更新
      isTeamMode: selectedMode === 'testcase', // 标记是否为团队模式
      isOrchestrationMode: selectedMode === 'orchestration', // 标记是否为编排模式
      agents: selectedMode === 'testcase' ? [] : undefined, // 团队模式下的智能体列表
    };

    setMessages(prev => [...prev, assistantMsg]);

    try {
      // 根据模式选择不同的 API 端点
      const endpoint = selectedMode === 'testcase'
        ? `${API_BASE_URL}/api/chat/testcase/stream`
        : selectedMode === 'orchestration'
        ? `${API_BASE_URL}/api/v1/normal_chat/stream_aitest`
        : `${API_BASE_URL}/api/chat/normal/stream`;

      // 根据模式构建不同的请求体
      let requestBody;
      if (selectedMode === 'orchestration') {
        // 编排模式使用新的 API 格式
        requestBody = {
          message: userMessage,
          session_id: conversationId,
          file_ids: fileIds.length > 0 ? fileIds : [],
          is_feedback: isFeedback
        };
        console.log('🚀 编排模式请求体:', JSON.stringify(requestBody, null, 2));
      } else {
        // 其他模式使用原有格式
        requestBody = {
          message: userMessage,
          file_ids: fileIds.length > 0 ? fileIds : undefined,
          is_feedback: isFeedback,
          conversation_id: conversationId,
          target_agent: targetAgent
        };
        console.log('🚀 其他模式请求体:', JSON.stringify(requestBody, null, 2));
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal, // 添加中止信号
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 从响应头中获取 conversation_id（不同模式使用不同的头部名称）
      const responseConversationId = selectedMode === 'orchestration'
        ? response.headers.get('x-session-id')
        : response.headers.get('X-Conversation-ID');
      console.log('📝 Conversation ID:', responseConversationId);

      // 保存会话 ID 到对应模式的状态和ref
      if (responseConversationId) {
        console.log('📝 准备保存会话ID:', responseConversationId, '到模式:', selectedMode);

        // 同时更新状态和ref，确保立即可用
        if (selectedMode === 'testcase') {
          setTestcaseConversationId(responseConversationId);
          testcaseSessionRef.current = responseConversationId;
          console.log('💾 测试模式会话ID已保存 (state + ref):', responseConversationId);
        } else if (selectedMode === 'orchestration') {
          setOrchestrationConversationId(responseConversationId);
          orchestrationSessionRef.current = responseConversationId;
          console.log('💾 编排模式会话ID已保存 (state + ref):', responseConversationId);

          // 立即验证状态更新
          setTimeout(() => {
            console.log('🔍 验证编排模式会话ID保存状态:');
            console.log('   State:', orchestrationConversationId);
            console.log('   Ref:', orchestrationSessionRef.current);
          }, 100);

          // 同时也在助手消息中保存会话ID作为备份
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMsgId
                ? { ...msg, sessionId: responseConversationId }
                : msg
            )
          );
        } else {
          setNormalConversationId(responseConversationId);
          normalSessionRef.current = responseConversationId;
          console.log('💾 普通模式会话ID已保存 (state + ref):', responseConversationId);
        }
        console.log('💾 已保存会话 ID 到', selectedMode, '模式:', responseConversationId);
      } else {
        console.warn('⚠️ 未收到会话ID响应头');
        console.warn('⚠️ 响应头列表:', Object.fromEntries(response.headers.entries()));
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantMsgId
                    ? { ...msg, streaming: false }
                    : msg
                )
              );
              continue;
            }

            try {
              const parsed = JSON.parse(data);

              // 团队模式的智能体消息处理
              if (parsed.type === 'agent_start') {
                // 智能体开始工作
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMsgId
                      ? {
                          ...msg,
                          agents: [
                            ...(msg.agents || []),
                            {
                              name: parsed.agent_name,
                              role: parsed.agent_role,
                              content: '',
                              collapsed: false,
                            }
                          ]
                        }
                      : msg
                  )
                );
              } else if (parsed.type === 'agent_message') {
                // 智能体消息更新
                setMessages(prev => {
                  const msg = prev.find(m => m.id === assistantMsgId);
                  if (!msg || !msg.agents) {
                    return prev;
                  }

                  const agentIndex = msg.agents.findIndex(a => a.name === parsed.agent_name);
                  if (agentIndex === -1) {
                    return prev;
                  }

                  // 后端已经发送累积的完整内容，前端直接使用，不再累加
                  const newContent = parsed.content || '';

                  return prev.map(m => {
                    if (m.id === assistantMsgId) {
                      const updatedAgents = [...m.agents];
                      updatedAgents[agentIndex] = {
                        ...updatedAgents[agentIndex],
                        content: newContent
                      };
                      return { ...m, agents: updatedAgents };
                    }
                    return m;
                  });
                });
              } else if (parsed.type === 'agent_done') {
                // 智能体完成工作
                setMessages(prev =>
                  prev.map(msg => {
                    if (msg.id === assistantMsgId && msg.agents) {
                      const updatedAgents = msg.agents.map(a =>
                        a.name === parsed.agent_name
                          ? { ...a, content: parsed.content, done: true }
                          : a
                      );
                      return { ...msg, agents: updatedAgents };
                    }
                    return msg;
                  })
                );
              } else if (parsed.type === 'feedback_request') {
                // 智能体请求用户反馈
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMsgId
                      ? {
                          ...msg,
                          feedbackRequest: {
                            agentName: parsed.agent_name,
                            agentRole: parsed.agent_role,
                            availableAgents: parsed.available_agents || []
                          },
                          conversationId: responseConversationId  // 保存会话 ID
                        }
                      : msg
                  )
                );
                // 停止流式传输
                setIsStreaming(false);
                setLoading(false);
              } else if (parsed.type === 'chunk') {
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMsgId
                      ? { ...msg, content: msg.content + parsed.content }
                      : msg
                  )
                );
              } else if (parsed.type === 'status') {
                // 编排模式的状态更新（如 "thinking"）
                if (selectedMode === 'orchestration') {
                  console.log('🔄 编排模式状态:', parsed.content);
                  // 可以在这里添加状态显示逻辑
                }
              } else if (parsed.type === 'message') {
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMsgId
                      ? { ...msg, content: parsed.content, streaming: false }
                      : msg
                  )
                );
              } else if (parsed.type === 'tokens' || parsed.type === 'token_usage') {
                // 处理 token 统计信息（支持两种格式）
                const tokenData = parsed.tokens || parsed;
                if (tokenData) {
                  setMessages(prev =>
                    prev.map(msg => {
                      // 更新用户消息的 token（只显示输入 token）
                      if (msg.role === 'user' && msg.content === userMessage) {
                        return { ...msg, tokens: { input: tokenData.input || tokenData.prompt_tokens } };
                      }
                      // 更新助手消息的 token（显示输出 token）
                      if (msg.id === assistantMsgId) {
                        return { ...msg, tokens: { output: tokenData.output || tokenData.completion_tokens } };
                      }
                      return msg;
                    })
                  );
                }
              } else if (parsed.type === 'error') {
                message.error(parsed.content);
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMsgId
                      ? { ...msg, content: `错误: ${parsed.content}`, streaming: false, error: true }
                      : msg
                  )
                );
              }
            } catch (e) {
              console.error('❌ 解析 SSE 数据失败:', e);
              console.error('   原始数据:', data);
            }
          }
        }
      }

    } catch (error) {
      // 如果是用户主动中止，不显示错误
      if (error.name === 'AbortError') {
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMsgId
              ? { ...msg, streaming: false }
              : msg
          )
        );
      } else {
        console.error('流式传输错误:', error);
        message.error('无法连接到服务器');
        setMessages(prev =>
          prev.map(msg =>
            msg.id === assistantMsgId
              ? { ...msg, content: '获取响应失败，请重试。', streaming: false, error: true }
              : msg
          )
        );
      }
    } finally {
      setLoading(false);
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleSend = (value) => {
    if (!value.trim()) return;

    // 检查是否有文件正在解析
    if (isParsing) {
      message.warning('文件正在解析中，请稍候...');
      return;
    }

    handleStreamingChat(value);
  };

  const handleSuggestionClick = (text) => {
    handleStreamingChat(text);
  };

  // 停止流式传输
  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      message.info('已停止生成');
    }
  };

  const handleClear = () => {
    setMessages([]);
    // 清除当前模式的会话 ID (同时清除state和ref)
    if (selectedMode === 'testcase') {
      setTestcaseConversationId(null);
      testcaseSessionRef.current = null;
    } else if (selectedMode === 'orchestration') {
      setOrchestrationConversationId(null);
      orchestrationSessionRef.current = null;
    } else {
      setNormalConversationId(null);
      normalSessionRef.current = null;
    }
    console.log('🧹 已清除', selectedMode, '模式的对话和会话ID');
    message.success('对话已清空');
  };

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    let modeText = '';
    if (mode === 'normal') {
      modeText = '后端普通模式';
    } else if (mode === 'orchestration') {
      modeText = '后端编排模式';
      console.log('🔄 切换到编排模式，当前会话ID:', orchestrationConversationId);
    } else if (mode === 'testcase') {
      modeText = '测试用例智能体';
    } else if (mode === 'image-analyzer') {
      modeText = 'UI 测试用例智能体';
    }
    message.success(`已进入${modeText}模式`);
  };

  const handleBackToModeSelector = () => {
    setSelectedMode(null);
    message.success('已返回模式选择');
  };

  // 处理智能体标签点击
  const handleAgentTagClick = (agentName) => {
    // 检查输入框中是否已经有 @ 提及
    const currentInput = inputValue.trim();
    const hasAtMention = currentInput.match(/@(TestCase_\w+|all)/i);

    if (hasAtMention) {
      // 如果已经有 @ 提及，替换它
      const newInput = currentInput.replace(/@(TestCase_\w+|all)/i, `@${agentName}`);
      setInputValue(newInput);
    } else {
      // 如果没有 @ 提及，添加到开头
      setInputValue(`@${agentName} ${currentInput}`);
    }

    message.success(`已选择 @${agentName}`);
  };

  // 处理清除 @ 提及
  const handleClearMention = () => {
    const currentInput = inputValue.trim();
    const newInput = currentInput.replace(/@(TestCase_\w+|all)\s*/i, '');
    setInputValue(newInput);
    message.success('已清除智能体选择');
  };

  // 1. 重新发送用户消息
  const handleResendMessage = async (messageId) => {
    const msg = messages.find(m => m.id === messageId);
    if (!msg || msg.role !== 'user') return;

    console.log('🔄 重新发送消息:', msg.content);
    await handleStreamingChat(msg.content);
    message.success('消息已重新发送');
  };

  // 2. 编辑用户消息
  const handleEditMessage = (messageId) => {
    const msg = messages.find(m => m.id === messageId);
    if (!msg || msg.role !== 'user') return;

    setEditingMessageId(messageId);
    setEditingContent(msg.content);
    console.log('✏️ 开始编辑消息:', messageId);
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingContent('');
    message.info('已取消编辑');
  };

  // 保存编辑并重新发送
  const handleSaveEdit = async (messageId) => {
    if (!editingContent.trim()) {
      message.warning('消息内容不能为空');
      return;
    }

    console.log('💾 保存编辑并重新发送:', editingContent);

    // 更新消息内容
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId ? { ...msg, content: editingContent } : msg
      )
    );

    // 重新发送
    await handleStreamingChat(editingContent);

    // 清除编辑状态
    setEditingMessageId(null);
    setEditingContent('');
    message.success('消息已更新并重新发送');
  };

  // 3. 复制智能体消息
  const handleCopyMessage = async (messageId) => {
    const msg = messages.find(m => m.id === messageId);
    if (!msg || msg.role !== 'assistant') return;

    try {
      let textToCopy = '';

      if (msg.isTeamMode && msg.agents) {
        // 团队模式：复制所有智能体的回答
        textToCopy = msg.agents
          .map(agent => `## ${agent.name}\n\n${agent.content}`)
          .join('\n\n---\n\n');
      } else {
        // 普通模式：复制单个回答
        textToCopy = msg.content;
      }

      await navigator.clipboard.writeText(textToCopy);
      message.success('已复制到剪贴板');
      console.log('📋 已复制消息');
    } catch (err) {
      console.error('复制失败:', err);
      message.error('复制失败');
    }
  };

  // 4. 保存智能体消息为 Markdown 文件
  const handleSaveMessage = (messageId) => {
    const msg = messages.find(m => m.id === messageId);
    if (!msg || msg.role !== 'assistant') return;

    try {
      let markdownContent = '';
      let filename = '';

      if (msg.isTeamMode && msg.agents) {
        // 团队模式：保存所有智能体的回答
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        filename = `testcase-team-${timestamp}.md`;

        markdownContent = `# 测试用例智能体团队回答\n\n`;
        markdownContent += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
        markdownContent += `---\n\n`;

        msg.agents.forEach(agent => {
          markdownContent += `## ${agent.name}\n\n`;
          markdownContent += `${agent.content}\n\n`;
          markdownContent += `---\n\n`;
        });
      } else {
        // 普通模式：保存单个回答
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        filename = `ai-response-${timestamp}.md`;

        markdownContent = `# AI 回答\n\n`;
        markdownContent += `生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
        markdownContent += `---\n\n`;
        markdownContent += msg.content;
      }

      // 创建 Blob 并下载
      const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      message.success(`已保存为 ${filename}`);
      console.log('💾 已保存消息为 Markdown 文件');
    } catch (err) {
      console.error('保存失败:', err);
      message.error('保存失败');
    }
  };

  const toggleAgentCollapse = (messageId, agentName) => {
    setCollapsedAgents(prev => ({
      ...prev,
      [messageId]: {
        ...(prev[messageId] || {}),
        [agentName]: !(prev[messageId]?.[agentName] || false)
      }
    }));
  };

  // 文件上传相关处理
  const handleFilesChange = (files) => {
    setUploadedFiles(files);
    // 如果文件列表为空，清空已解析的文件
    if (files.length === 0) {
      setParsedFiles([]);
    }
  };

  const handleParsingStart = () => {
    setIsParsing(true);
  };

  const handleParsingComplete = (parsed) => {
    // 更新已解析的文件列表
    setParsedFiles(prev => {
      // 合并新解析的文件和之前的文件
      const newParsed = [...prev];
      parsed.forEach(p => {
        const index = newParsed.findIndex(f => f.uid === p.uid);
        if (index >= 0) {
          newParsed[index] = p;
        } else {
          newParsed.push(p);
        }
      });
      return newParsed;
    });

    // 检查是否所有文件都已解析完成
    const allParsed = uploadedFiles.every(file => {
      const parsedFile = [...parsedFiles, ...parsed].find(f => f.uid === file.uid);
      return parsedFile && !parsedFile.parsing;
    });

    if (allParsed) {
      setIsParsing(false);
    }
  };

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  };

  // Markdown 组件配置
  const MarkdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={isDark ? vscDarkPlus : vs}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
          borderRadius: 16,
          fontSize: 15,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
      }}
    >
      <AntApp>
        {/* 如果未选择模式，显示模式选择页面 */}
        {!selectedMode ? (
          <div className={`mode-selector-wrapper ${isDark ? 'dark' : 'light'}`}>
            {/* 矩阵雨背景 */}
            <MatrixRain isDark={isDark} />

            {/* 动态背景 */}
            <div className="animated-background">
              <div className="gradient-orb orb-1"></div>
              <div className="gradient-orb orb-2"></div>
              <div className="gradient-orb orb-3"></div>
            </div>

            {/* 主题切换按钮（浮动按钮）*/}
            <FloatButton
              icon={isDark ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              style={{ right: 24, bottom: 24 }}
              tooltip={isDark ? '切换到浅色主题' : '切换到深色主题'}
            />

            {/* 模式选择页面 */}
            <ModeSelector onSelectMode={handleModeSelect} isDark={isDark} onToggleTheme={toggleTheme} />
          </div>
        ) : selectedMode === 'image-analyzer' ? (
          // 图片分析模式
          <div className={`app-container image-analyzer-mode ${isDark ? 'dark' : 'light'}`}>
            {/* 矩阵雨背景 */}
            <MatrixRain isDark={isDark} />

            {/* 动态背景 */}
            <div className="animated-background">
              <div className="gradient-orb orb-1"></div>
              <div className="gradient-orb orb-2"></div>
              <div className="gradient-orb orb-3"></div>
            </div>

            {/* 顶部导航栏 */}
            <motion.header
              className="app-header"
              initial={{ y: -100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              <div className="header-content">
                <div className="logo-section">
                  <motion.div
                    className="logo-icon-wrapper"
                    whileHover={{ scale: 1.1, rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <FireOutlined className="logo-icon" />
                  </motion.div>
                  <div className="logo-text">
                    <h1 className="logo-title">UI 图片分析智能体团队</h1>
                    <p className="logo-subtitle">图片分析生成UI自动化脚本</p>
                  </div>
                </div>

                <div className="header-actions">
                  <motion.button
                    className="icon-button"
                    onClick={handleBackToModeSelector}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    title="返回模式选择"
                  >
                    <HomeOutlined />
                  </motion.button>
                  <motion.button
                    className="icon-button"
                    onClick={toggleTheme}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isDark ? <SunOutlined /> : <MoonOutlined />}
                  </motion.button>
                </div>
              </div>
            </motion.header>

            {/* 图片分析组件 */}
            <ImageAnalyzer isDark={isDark} />
          </div>
        ) : (
          <div className={`app-container ${isDark ? 'dark' : 'light'}`}>
            {/* 矩阵雨背景 */}
            <MatrixRain isDark={isDark} />

            {/* 动态背景（保留但降低透明度）*/}
            <div className="animated-background">
              <div className="gradient-orb orb-1"></div>
              <div className="gradient-orb orb-2"></div>
              <div className="gradient-orb orb-3"></div>
            </div>

            {/* 顶部导航栏 */}
            <motion.header
              className="app-header"
              initial={{ y: -100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              <div className="header-content">
                <div className="logo-section">
                  <motion.div
                    className="logo-icon-wrapper"
                    whileHover={{ scale: 1.1, rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <FireOutlined className="logo-icon" />
                  </motion.div>
                  <div className="logo-text">
                    <h1 className="logo-title">
                      {selectedMode === 'testcase' ? '🧪 测试用例智能体团队' :
                       selectedMode === 'orchestration' ? '🤖 AutoGen 编排模式' : 'DeepSeek AI'}
                    </h1>
                    <p className="logo-subtitle">
                      {selectedMode === 'testcase' ? '专业测试用例生成服务' :
                       selectedMode === 'orchestration' ? '智能体编排对话系统，利用 AutoGen 框架的消息机制实现对话传递' : '智能对话助手'}
                    </p>

                  </div>
                </div>

                <div className="header-actions">
                  <motion.button
                    className="icon-button"
                    onClick={handleBackToModeSelector}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    title="返回模式选择"
                  >
                    <HomeOutlined />
                  </motion.button>
                  <motion.button
                    className="icon-button"
                    onClick={toggleTheme}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isDark ? <SunOutlined /> : <MoonOutlined />}
                  </motion.button>
                  <motion.button
                    className="icon-button"
                    onClick={handleClear}
                    disabled={messages.length === 0}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <ClearOutlined />
                  </motion.button>
                </div>
              </div>
            </motion.header>

          {/* 主内容区域 */}
          <main className="app-main">
            <div
              ref={messagesContainerRef}
              className="chat-container"
              onScroll={handleScroll}
            >
              <AnimatePresence mode="wait">
                {messages.length === 0 ? (
                  <motion.div
                    className="welcome-section"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5 }}
                  >
                    <motion.div
                      className="welcome-icon"
                      animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, 5, -5, 0]
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: 'easeInOut'
                      }}
                    >
                      {selectedMode === 'testcase' ? <TeamOutlined /> :
                       selectedMode === 'orchestration' ? <RobotOutlined /> : <RocketOutlined />}
                    </motion.div>

                    <motion.h2
                      className="welcome-title"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      {selectedMode === 'testcase' ? '🧪 测试用例智能体团队' :
                       selectedMode === 'orchestration' ? '🤖 AutoGen 编排模式' : '你好！我是 DeepSeek AI 助手'}
                    </motion.h2>

                    <motion.p
                      className="welcome-subtitle"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                    >
                      {selectedMode === 'testcase'
                        ? '由 3 个专业智能体协作，为您生成高质量的测试用例'
                        : selectedMode === 'orchestration'
                        ? '基于 AutoGen 框架的智能体编排系统，提供更智能的对话体验'
                        : '我可以帮你解答问题、编写代码、创作内容等等'
                      }
                    </motion.p>

                    <motion.div
                      className="suggestions-grid"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 }}
                    >
                      {(selectedMode === 'testcase' ? TESTCASE_SUGGESTIONS :
                        selectedMode === 'orchestration' ? ORCHESTRATION_SUGGESTIONS : SUGGESTIONS).map((suggestion, index) => (
                        <motion.div
                          key={index}
                          className="suggestion-card"
                          onClick={() => handleSuggestionClick(suggestion.text)}
                          style={{ background: suggestion.gradient }}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.5 + index * 0.1 }}
                          whileHover={{
                            scale: 1.05,
                            boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
                          }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <div className="suggestion-emoji">{suggestion.emoji}</div>
                          <div className="suggestion-text">{suggestion.text}</div>
                        </motion.div>
                      ))}
                    </motion.div>
                  </motion.div>
                ) : (
                  <motion.div
                    className="messages-container"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                  >
                    <AnimatePresence>
                      {messages.map((msg, index) => (
                        <motion.div
                          key={msg.id}
                          className={`message-wrapper ${msg.role}`}
                          initial={{ opacity: 0, y: 20, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                        >
                          {/* 消息操作按钮 */}
                          {msg.role === 'user' && (
                            <motion.div
                              className="message-actions user-actions"
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.2 }}
                            >
                              <motion.button
                                className="action-button"
                                onClick={() => handleResendMessage(msg.id)}
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                title="重新发送"
                              >
                                <RedoOutlined />
                              </motion.button>
                              <motion.button
                                className="action-button"
                                onClick={() => handleEditMessage(msg.id)}
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                title="编辑消息"
                              >
                                <EditOutlined />
                              </motion.button>
                            </motion.div>
                          )}

                          {msg.role === 'assistant' && !msg.streaming && (
                            <motion.div
                              className="message-actions assistant-actions"
                              initial={{ opacity: 0, x: 10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.2 }}
                            >
                              <motion.button
                                className="action-button"
                                onClick={() => handleCopyMessage(msg.id)}
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                title="复制内容"
                              >
                                <CopyOutlined />
                              </motion.button>
                              <motion.button
                                className="action-button"
                                onClick={() => handleSaveMessage(msg.id)}
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                title="保存为 Markdown"
                              >
                                <SaveOutlined />
                              </motion.button>
                            </motion.div>
                          )}

                          <div className={`message-bubble ${msg.role}`}>
                            <div className="message-avatar">
                              {msg.role === 'assistant' ? (
                                <div className="avatar-icon assistant">
                                  <RobotOutlined />
                                </div>
                              ) : (
                                <div className="avatar-icon user">
                                  <span>👤</span>
                                </div>
                              )}
                            </div>

                            <div className="message-content">
                              {msg.role === 'assistant' ? (
                                <>
                                  {/* 团队模式：显示智能体列表 */}
                                  {msg.isTeamMode && msg.agents && msg.agents.length > 0 ? (
                                    <div className="team-agents-container">
                                      {msg.agents.map((agent, agentIndex) => {
                                        const isCollapsed = collapsedAgents[msg.id]?.[agent.name] || false;
                                        return (
                                          <motion.div
                                            key={agentIndex}
                                            className="agent-section"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: agentIndex * 0.1 }}
                                          >
                                            <div
                                              className="agent-header"
                                              onClick={() => toggleAgentCollapse(msg.id, agent.name)}
                                            >
                                              <div className="agent-info">
                                                <span className="agent-role">{agent.role}</span>
                                                <span className="agent-name">{agent.name}</span>
                                              </div>
                                              <motion.div
                                                className="collapse-icon"
                                                animate={{ rotate: isCollapsed ? 0 : 180 }}
                                                transition={{ duration: 0.3 }}
                                              >
                                                ▼
                                              </motion.div>
                                            </div>
                                            <motion.div
                                              className="agent-content"
                                              initial={false}
                                              animate={{
                                                maxHeight: isCollapsed ? 0 : 'none',
                                                opacity: isCollapsed ? 0 : 1,
                                                paddingTop: isCollapsed ? 0 : 8,
                                                paddingBottom: isCollapsed ? 0 : 18
                                              }}
                                              transition={{ duration: 0.3, ease: 'easeInOut' }}
                                              style={{
                                                overflow: isCollapsed ? 'hidden' : 'visible'
                                              }}
                                            >
                                              <div className="markdown-wrapper">
                                                <ReactMarkdown
                                                  remarkPlugins={[remarkGfm]}
                                                  components={MarkdownComponents}
                                                >
                                                  {agent.content || ''}
                                                </ReactMarkdown>
                                                {!agent.done && msg.streaming && (
                                                  <motion.span
                                                    className="typing-cursor"
                                                    animate={{ opacity: [1, 0, 1] }}
                                                    transition={{ duration: 1, repeat: Infinity }}
                                                  >
                                                    ▊
                                                  </motion.span>
                                                )}
                                              </div>
                                            </motion.div>
                                          </motion.div>
                                        );
                                      })}

                                      {/* 反馈请求对话框 */}
                                      {msg.feedbackRequest && (
                                        <motion.div
                                          className="feedback-dialog"
                                          initial={{ opacity: 0, y: 20 }}
                                          animate={{ opacity: 1, y: 0 }}
                                          transition={{ duration: 0.3 }}
                                        >
                                          <div className="feedback-header">
                                            <span className="feedback-icon">💬</span>
                                            <span className="feedback-title">
                                              {msg.feedbackRequest.agentRole} 已完成，请提供反馈
                                            </span>
                                          </div>
                                          <div className="feedback-hint">
                                            <p>• 直接点击"同意"，Optimizer 将给出最终优化方案</p>
                                            <p>• 点击下方智能体标签，指定特定智能体回答</p>
                                            <p>• 点击"All"，重新运行 Generator → Reviewer 流程</p>
                                          </div>

                                          {/* 智能体标签选择器 */}
                                          <div className="agent-tags-container">
                                            <div className="agent-tags-label">选择智能体：</div>
                                            <div className="agent-tags">
                                              {/* All 标签 */}
                                              <motion.button
                                                className="agent-tag agent-tag-all"
                                                onClick={() => handleAgentTagClick('all')}
                                                whileHover={{ scale: 1.05 }}
                                                whileTap={{ scale: 0.95 }}
                                              >
                                                <span className="agent-tag-icon">🔄</span>
                                                <span className="agent-tag-name">All</span>
                                              </motion.button>

                                              {/* 智能体标签 */}
                                              {msg.feedbackRequest.availableAgents.map((agentName, index) => (
                                                <motion.button
                                                  key={agentName}
                                                  className="agent-tag"
                                                  onClick={() => handleAgentTagClick(agentName)}
                                                  whileHover={{ scale: 1.05 }}
                                                  whileTap={{ scale: 0.95 }}
                                                  style={{ animationDelay: `${index * 0.1}s` }}
                                                >
                                                  <span className="agent-tag-icon">
                                                    {agentName.includes('Generator') ? '🎯' :
                                                     agentName.includes('Reviewer') ? '🔍' :
                                                     agentName.includes('Optimizer') ? '⚡' : '🤖'}
                                                  </span>
                                                  <span className="agent-tag-name">
                                                    {agentName.replace('TestCase_', '')}
                                                  </span>
                                                </motion.button>
                                              ))}

                                              {/* 清除按钮 */}
                                              {inputValue.match(/@(TestCase_\w+|all)/i) && (
                                                <motion.button
                                                  className="agent-tag agent-tag-clear"
                                                  onClick={handleClearMention}
                                                  whileHover={{ scale: 1.05 }}
                                                  whileTap={{ scale: 0.95 }}
                                                  initial={{ opacity: 0, scale: 0.8 }}
                                                  animate={{ opacity: 1, scale: 1 }}
                                                >
                                                  <span className="agent-tag-icon">✖️</span>
                                                  <span className="agent-tag-name">清除</span>
                                                </motion.button>
                                              )}
                                            </div>
                                          </div>

                                          <div className="feedback-actions">
                                            <motion.button
                                              className="approve-button"
                                              onClick={() => handleApprove(msg.id)}
                                              whileHover={{ scale: 1.05 }}
                                              whileTap={{ scale: 0.95 }}
                                            >
                                              ✅ 同意
                                            </motion.button>
                                          </div>
                                        </motion.div>
                                      )}
                                    </div>
                                  ) : (
                                    /* 普通模式：显示单个回复 */
                                    <div className="markdown-wrapper">
                                      <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={MarkdownComponents}
                                      >
                                        {msg.content || ''}
                                      </ReactMarkdown>
                                      {msg.streaming && (
                                        <motion.span
                                          className="typing-cursor"
                                          animate={{ opacity: [1, 0, 1] }}
                                          transition={{ duration: 1, repeat: Infinity }}
                                        >
                                          ▊
                                        </motion.span>
                                      )}
                                    </div>
                                  )}
                                  <div className="message-meta">
                                    {msg.timestamp && (
                                      <span className="timestamp-info">
                                        {formatTimestamp(msg.timestamp)}
                                      </span>
                                    )}
                                    {msg.tokens && msg.tokens.output && (
                                      <span className="token-info">
                                        Tokens: ↓{msg.tokens.output}
                                      </span>
                                    )}
                                  </div>
                                </>
                              ) : (
                                <>
                                  {editingMessageId === msg.id ? (
                                    // 编辑模式
                                    <div className="edit-message-container">
                                      <textarea
                                        className="edit-message-textarea"
                                        value={editingContent}
                                        onChange={(e) => setEditingContent(e.target.value)}
                                        autoFocus
                                        rows={4}
                                      />
                                      <div className="edit-message-actions">
                                        <motion.button
                                          className="edit-action-button save"
                                          onClick={() => handleSaveEdit(msg.id)}
                                          whileHover={{ scale: 1.05 }}
                                          whileTap={{ scale: 0.95 }}
                                        >
                                          <CheckOutlined /> 保存并发送
                                        </motion.button>
                                        <motion.button
                                          className="edit-action-button cancel"
                                          onClick={handleCancelEdit}
                                          whileHover={{ scale: 1.05 }}
                                          whileTap={{ scale: 0.95 }}
                                        >
                                          <CloseOutlined /> 取消
                                        </motion.button>
                                      </div>
                                    </div>
                                  ) : (
                                    // 正常显示模式
                                    <>
                                      <div className="user-message-text">
                                        {msg.hasFiles && msg.fileCount > 0 && (
                                          <div className="file-context-badge">
                                            <PaperClipOutlined /> 包含 {msg.fileCount} 个文件
                                          </div>
                                        )}
                                        {msg.content}
                                      </div>
                                      <div className="message-meta">
                                        {msg.timestamp && (
                                          <span className="timestamp-info">
                                            {formatTimestamp(msg.timestamp)}
                                          </span>
                                        )}
                                        {msg.tokens && msg.tokens.input && (
                                          <span className="token-info">
                                            Tokens: ↑{msg.tokens.input}
                                          </span>
                                        )}
                                      </div>
                                    </>
                                  )}
                                </>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                    <div ref={messagesEndRef} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </main>

          {/* 输入区域 */}
          <motion.footer
            className="app-footer"
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            {/* 文件上传区域 - 仅在测试用例模式显示 */}
            {selectedMode === 'testcase' && (
              <div className="file-upload-wrapper">
                <FileUpload
                  onFilesChange={handleFilesChange}
                  onParsingStart={handleParsingStart}
                  onParsingComplete={handleParsingComplete}
                  disabled={loading || isStreaming}
                />
              </div>
            )}

            <div className="input-container">
              <Sender
                className="message-sender"
                placeholder={
                  isParsing
                    ? "正在解析文件，解析完成后才能发送..."
                    : parsedFiles.filter(f => f.success && f.file_id).length > 0
                      ? `已加载 ${parsedFiles.filter(f => f.success && f.file_id).length} 个文件，输入问题...`
                      : "输入消息，按 Enter 发送..."
                }
                onSubmit={handleSend}
                loading={loading || isParsing}
                value={inputValue}
                onChange={setInputValue}
                disabled={false}
                readOnly={false}
                prefix={
                  <motion.div
                    whileHover={{ scale: isParsing ? 1 : 1.2, rotateY: isParsing ? 0 : 180 }}
                    transition={{ duration: 0.3 }}
                    style={{ opacity: isParsing ? 0.5 : 1 }}
                  >
                    <SendOutlined />
                  </motion.div>
                }
                onCancel={isStreaming ? handleStop : undefined}
                allowSpeech={false}
              />
            </div>
          </motion.footer>

          {/* 浮动按钮 */}
          <FloatButton.Group
            trigger="hover"
            type="primary"
            style={{ right: 24, bottom: 24 }}
            icon={<StarOutlined />}
          >
            <FloatButton icon={<HeartOutlined />} tooltip="喜欢" />
            <FloatButton icon={<RocketOutlined />} tooltip="快速开始" />
          </FloatButton.Group>
          </div>
        )}
      </AntApp>
    </ConfigProvider>
  );
}

export default App;

