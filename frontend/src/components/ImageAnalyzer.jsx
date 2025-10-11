import React, { useState, useRef, useEffect } from 'react';
import { Upload, Button, Input, Card, Spin, message, Space, Collapse, Tag } from 'antd';
import {
  UploadOutlined,
  SendOutlined,
  ClearOutlined,
  PictureOutlined,
  LinkOutlined,
  FileImageOutlined,
  StopOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ImageAnalyzer.css';

const { TextArea } = Input;

// API 配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ImageAnalyzer = ({ isDark }) => {
  const [imageFile, setImageFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [testDescription, setTestDescription] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [agentMessages, setAgentMessages] = useState([]);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [expandedAgents, setExpandedAgents] = useState(['UI_Expert']); // 默认展开 UI 专家
  const [inputPanelsExpanded, setInputPanelsExpanded] = useState(['image-source']); // 输入面板展开状态（默认只展开图片来源）
  const [autoScroll, setAutoScroll] = useState(true); // 是否自动滚动
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const abortControllerRef = useRef(null);
  const lastScrollTopRef = useRef(0); // 记录上次滚动位置
  const isUserScrollingRef = useRef(false); // 标记用户是否正在滚动

  // 缓存并行智能体的结果，用于顺序展示
  const agentBufferRef = useRef({
    UI_Expert: { role: '', content: '', completed: false, started: false },
    Interaction_Analyst: { role: '', content: '', completed: false, started: false },
    Test_Scenario_Expert: { role: '', content: '', completed: false, started: false }
  });
  const canDisplayRef = useRef({
    UI_Expert: true,  // UI_Expert 总是可以立即显示
    Interaction_Analyst: false,  // 等 UI_Expert 完成
    Test_Scenario_Expert: false  // 等前两个完成
  });

  // 跟踪每个智能体是否已经完成过（用于控制展开逻辑）
  const agentCompletedOnceRef = useRef({
    UI_Expert: false,
    Interaction_Analyst: false,
    Test_Scenario_Expert: false
  });

  // 监听 expandedAgents 变化（调试用）
  // useEffect(() => {
  //   console.log('📊 expandedAgents 状态变化:', expandedAgents);
  // }, [expandedAgents]);

  // 消息变化时滚动到底部（仅当自动滚动开启时）
  useEffect(() => {
    if (autoScroll && messagesEndRef.current && !isUserScrollingRef.current) {
      // 使用 setTimeout 确保 DOM 已更新
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [agentMessages, autoScroll]);

  // 监听用户滚动事件
  const handleScroll = (e) => {
    const container = e.target;
    const currentScrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;

    // 判断是否在底部（允许 50px 的误差）
    const isAtBottom = scrollHeight - currentScrollTop - clientHeight < 50;
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

    // 500ms 后重置用户滚动标记
    setTimeout(() => {
      isUserScrollingRef.current = false;
    }, 500);
  };

  // 滚动到底部（保留原有函数，供手动调用）
  // 只有在自动滚动开启时才滚动
  const scrollToBottom = () => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // 处理图片上传
  const handleImageUpload = (file) => {
    setImageFile(file);
    setImageUrl(''); // 清空 URL
    message.success(`已选择图片: ${file.name}`);
    return false; // 阻止自动上传
  };

  // 清空表单
  const handleClear = () => {
    setImageFile(null);
    setImageUrl('');
    setWebUrl('');
    setTestDescription('');
    setAdditionalContext('');
    setAnalysisResults(null);
    setAgentMessages([]);
    setCurrentAgent(null);
    setExpandedAgents(['UI_Expert']); // 重置展开状态
  };

  // 发送分析请求
  const handleAnalyze = async () => {
    if (!imageFile && !imageUrl) {
      message.error('请上传图片或提供图片 URL');
      return;
    }

    setLoading(true);
    setAnalysisResults(null);
    setAgentMessages([]);
    setCurrentAgent(null);

    // 重置展开状态：默认展开 UI 专家，折叠其他
    // console.log('🔄 重置展开状态前，当前 expandedAgents:', expandedAgents);
    setExpandedAgents(['UI_Expert']);
    // console.log('🔄 重置展开状态，只展开 UI_Expert');

    // 折叠输入面板
    setInputPanelsExpanded([]);

    // 重置缓冲区和显示权限
    agentBufferRef.current = {
      UI_Expert: { role: '', content: '', completed: false, started: false },
      Interaction_Analyst: { role: '', content: '', completed: false, started: false },
      Test_Scenario_Expert: { role: '', content: '', completed: false, started: false }
    };
    canDisplayRef.current = {
      UI_Expert: true,
      Interaction_Analyst: false,
      Test_Scenario_Expert: false
    };

    // 重置完成标志
    agentCompletedOnceRef.current = {
      UI_Expert: false,
      Interaction_Analyst: false,
      Test_Scenario_Expert: false
    };
    // console.log('🔄 重置完成标志:', agentCompletedOnceRef.current);

    // console.log('🔄 开始新的分析，已清空所有状态和消息');

    // 创建 AbortController
    abortControllerRef.current = new AbortController();

    try {
      // 构建 FormData
      const formData = new FormData();

      if (imageFile) {
        formData.append('image', imageFile);
      }
      if (imageUrl) {
        formData.append('image_url', imageUrl);
      }
      if (webUrl) {
        formData.append('web_url', webUrl);
      }
      if (testDescription) {
        formData.append('test_description', testDescription);
      }
      if (additionalContext) {
        formData.append('additional_context', additionalContext);
      }

      // 发送流式请求
      const response = await fetch(`${API_BASE_URL}/api/image-analysis/stream`, {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 处理 SSE 流
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log('✅ SSE 流读取完成');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);

            if (data === '[DONE]') {
              console.log('✅ 收到 [DONE] 信号');
              setLoading(false);
              message.success('图片分析完成！');
              continue;
            }

            try {
              const event = JSON.parse(data);
              console.log('📨 SSE Event:', event.type, event.agent_name || '',
                         event.type === 'agent_message' ? `内容长度: ${event.content?.length}` : '');
              handleSSEEvent(event);
            } catch (e) {
              console.error('❌ 解析 SSE 事件失败:', e);
              console.error('   原始数据:', data);
            }
          }
        }
      }

      console.log('✅ SSE 处理循环结束');

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('⚠️ 分析被用户停止');
        message.warning('分析已停止');
      } else {
        console.error('❌ 分析失败:', error);
        console.error('   错误堆栈:', error.stack);
        message.error(`分析失败: ${error.message}`);
      }
      setLoading(false);
    } finally {
      console.log('🔄 清理 abortController');
      abortControllerRef.current = null;
    }
  };

  // 停止分析
  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setLoading(false);
      message.info('正在停止分析...');
    }
  };

  // 处理 SSE 事件
  const handleSSEEvent = (event) => {
    console.log('SSE Event:', event);

    switch (event.type) {
      case 'status':
        message.info(event.content);
        break;

      case 'agent_start':
        const agentName = event.agent_name;
        const agentRole = event.agent_role;

        console.log(`🚀 ${agentName} 开始，可显示: ${canDisplayRef.current[agentName]}`);

        // 更新缓冲区
        agentBufferRef.current[agentName] = {
          role: agentRole,
          content: '',
          completed: false,
          started: true
        };

        // 如果可以显示，检查是否已经有该智能体的气泡
        if (canDisplayRef.current[agentName]) {
          setAgentMessages(prev => {
            // 检查是否已经存在该智能体的消息
            const existingMessage = prev.find(msg => msg.agent_name === agentName);

            if (existingMessage) {
              // 已经存在，不创建新气泡，只重置状态
              console.log(`⚠️ ${agentName} 的气泡已存在，不创建新气泡，只重置状态`);
              return prev.map(msg =>
                msg.agent_name === agentName
                  ? { ...msg, status: 'processing', content: '' }
                  : msg
              );
            } else {
              // 不存在，创建新气泡
              console.log(`✅ 创建 ${agentName} 的新气泡`);
              return [...prev, {
                agent_name: agentName,
                agent_role: agentRole,
                content: '',
                status: 'processing',
                timestamp: new Date().toISOString()
              }];
            }
          });

          // Test_Scenario_Expert 在开始时自动展开
          if (agentName === 'Test_Scenario_Expert') {
            setExpandedAgents(prev => {
              // console.log('🎯 Test_Scenario_Expert 开始，自动展开，当前展开列表:', prev);
              if (!prev.includes('Test_Scenario_Expert')) {
                return [...prev, 'Test_Scenario_Expert'];
              }
              return prev;
            });
          }

          scrollToBottom();
        } // else {
          // console.log(`⏸️ ${agentName} 开始但不可显示，缓存中`);
        // }
        break;

      case 'agent_message':
        const msgAgentName = event.agent_name;
        const content = event.content;

        console.log(`📨 收到 ${msgAgentName} 的消息，长度: ${content?.length || 0}, 可显示: ${canDisplayRef.current[msgAgentName]}`);

        // 更新缓冲区
        if (agentBufferRef.current[msgAgentName]) {
          agentBufferRef.current[msgAgentName].content = content;
        } else {
          console.warn(`⚠️ ${msgAgentName} 的缓冲区不存在`);
        }

        // 如果可以显示，实时更新内容
        if (canDisplayRef.current[msgAgentName]) {
          setAgentMessages(prev => {
            const newMessages = [...prev];

            // 先查找该智能体对应的 processing 消息
            let messageIndex = newMessages.findIndex(msg => msg.agent_name === msgAgentName && msg.status === 'processing');

            // 如果没找到 processing 消息，查找任何状态的消息
            if (messageIndex === -1) {
              messageIndex = newMessages.findIndex(msg => msg.agent_name === msgAgentName);
            }

            if (messageIndex !== -1) {
              // 找到了，更新该消息的内容
              console.log(`📝 更新 ${msgAgentName} 的消息，内容长度: ${content?.length || 0}`);
              newMessages[messageIndex] = {
                ...newMessages[messageIndex],
                content: content,
                // 始终保持 'processing' 状态，直到收到 'done' 事件
                status: 'processing'
              };
            } else {
              // 真的没找到，创建新消息（这种情况不应该发生）
              console.warn(`⚠️ 未找到 ${msgAgentName} 的任何消息，创建新消息`);
              newMessages.push({
                agent_name: msgAgentName,
                agent_role: agentBufferRef.current[msgAgentName]?.role || msgAgentName,
                content: content,
                status: 'processing',
                timestamp: new Date().toISOString()
              });
            }

            return newMessages;
          });
          scrollToBottom();
        } else {
          console.log(`⏸️ ${msgAgentName} 的消息被缓存（不可显示）`);
        }
        break;

      case 'agent_done':
        const doneAgentName = event.agent_name;

        console.log(`✅ ${doneAgentName} 完成`);

        // 标记完成（仅用于缓冲区）
        if (agentBufferRef.current[doneAgentName]) {
          agentBufferRef.current[doneAgentName].completed = true;
        }

        // 不改变状态，保持 'processing'
        // 只有收到 'done' 事件（所有分析完成）时才改为 'done'

        // 解锁下一个智能体的显示权限（只在第一次完成时）
        if (doneAgentName === 'UI_Expert' && !agentCompletedOnceRef.current.UI_Expert) {
          console.log('✅ UI_Expert 第一次完成，解锁 Interaction_Analyst');
          agentCompletedOnceRef.current.UI_Expert = true;
          canDisplayRef.current.Interaction_Analyst = true;

          // UI 专家完成后，展开交互分析师
          setExpandedAgents(prev => {
            if (!prev.includes('Interaction_Analyst')) {
              return [...prev, 'Interaction_Analyst'];
            }
            return prev;
          });

          // ⚠️ 不要在这里创建 Interaction_Analyst 的消息气泡
          // 因为 agent_start 事件会创建气泡
          // 这里只需要解锁显示权限和展开折叠面板即可

        } else if (doneAgentName === 'Interaction_Analyst' && !agentCompletedOnceRef.current.Interaction_Analyst) {
          console.log('✅ Interaction_Analyst 第一次完成，解锁 Test_Scenario_Expert');
          agentCompletedOnceRef.current.Interaction_Analyst = true;
          canDisplayRef.current.Test_Scenario_Expert = true;

          // 不在这里展开 Test_Scenario_Expert
          // 因为 UI_Expert 和 Interaction_Analyst 可能会多次切换
          // Test_Scenario_Expert 会在它自己的 agent_start 事件中展开
        }
        break;

      case 'error':
        message.error(event.content);
        setLoading(false);
        break;

      case 'done':
        // 所有分析完成，将所有智能体标记为完成
        // console.log('✅ 所有分析完成，标记所有智能体为完成');
        setAgentMessages(prev => {
          return prev.map(msg => ({
            ...msg,
            status: 'done'
          }));
        });
        setLoading(false);
        break;

      case 'token_usage':
        console.log('Token usage:', event.token_usage);
        break;

      default:
        console.log('Unknown event type:', event.type);
    }
  };

  // 渲染智能体消息
  const renderAgentMessage = (msg, index) => {
    const isProcessing = msg.status === 'processing';
    const isDone = msg.status === 'done';
    const isExpanded = expandedAgents.includes(msg.agent_name);

    // console.log(`🎨 渲染 ${msg.agent_name}，展开状态: ${isExpanded}，expandedAgents:`, expandedAgents);

    // 切换折叠状态
    const toggleExpand = () => {
      setExpandedAgents(prev => {
        if (prev.includes(msg.agent_name)) {
          return prev.filter(name => name !== msg.agent_name);
        } else {
          return [...prev, msg.agent_name];
        }
      });
    };

    // 使用 items 属性而不是 Panel 子组件
    const items = [
      {
        key: msg.agent_name,
        label: (
          <Space>
            <span className="agent-role">{msg.agent_role}</span>
            <Tag color={isProcessing ? 'processing' : 'success'}>
              {isProcessing ? '分析中...' : '完成'}
            </Tag>
          </Space>
        ),
        children: (
          <div className="agent-message-content">
            {msg.content ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            ) : (
              <div style={{ color: '#999', fontStyle: 'italic' }}>
                等待智能体回复...
              </div>
            )}
          </div>
        )
      }
    ];

    return (
      <Collapse
        key={index}
        activeKey={isExpanded ? [msg.agent_name] : []}
        onChange={toggleExpand}
        className="agent-message-collapse"
        items={items}
      />
    );
  };

  return (
    <div className={`image-analyzer ${isDark ? 'dark' : 'light'}`}>
      <Card title="🖼️ UI 图片分析" className="analyzer-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 图片上传区域 - 可折叠 */}
          <Collapse
            activeKey={inputPanelsExpanded}
            onChange={setInputPanelsExpanded}
            items={[
              {
                key: 'image-source',
                label: '📸 图片来源',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Upload
                      accept="image/*"
                      beforeUpload={handleImageUpload}
                      fileList={imageFile ? [imageFile] : []}
                      onRemove={() => setImageFile(null)}
                      maxCount={1}
                    >
                      <Button icon={<UploadOutlined />} disabled={loading}>
                        上传图片文件
                      </Button>
                    </Upload>

                    <Input
                      placeholder="或者输入图片 URL"
                      prefix={<LinkOutlined />}
                      value={imageUrl}
                      onChange={(e) => {
                        setImageUrl(e.target.value);
                        setImageFile(null); // 清空文件
                      }}
                      disabled={loading}
                    />
                  </Space>
                )
              },
              {
                key: 'additional-info',
                label: '📝 附加信息（可选）',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Input
                      placeholder="图片所在页面 URL"
                      prefix={<LinkOutlined />}
                      value={webUrl}
                      onChange={(e) => setWebUrl(e.target.value)}
                      disabled={loading}
                    />

                    <TextArea
                      placeholder="测试场景描述"
                      rows={2}
                      value={testDescription}
                      onChange={(e) => setTestDescription(e.target.value)}
                      disabled={loading}
                    />

                    <TextArea
                      placeholder="附加上下文信息"
                      rows={2}
                      value={additionalContext}
                      onChange={(e) => setAdditionalContext(e.target.value)}
                      disabled={loading}
                    />
                  </Space>
                )
              }
            ]}
          />

          {/* 操作按钮 */}
          <Space>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleAnalyze}
              loading={loading}
              disabled={(!imageFile && !imageUrl) || loading}
            >
              开始分析
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClear}
              disabled={loading}
            >
              清空
            </Button>
          </Space>

          {/* 分析结果 */}
          {agentMessages.length > 0 && (
            <Card type="inner" title="📊 分析结果" size="small">
              <div
                className="agent-messages-container"
                ref={messagesContainerRef}
                onScroll={handleScroll}
              >
                {agentMessages.map((msg, index) => renderAgentMessage(msg, index))}
                {loading && (
                  <div className="loading-indicator">
                    <Spin />
                    <div style={{ marginTop: '8px', color: '#999' }}>分析中...</div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* 停止分析按钮 - 放在气泡最下面 */}
              {loading && (
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                  <Button
                    danger
                    icon={<StopOutlined />}
                    onClick={handleStop}
                    size="large"
                  >
                    停止分析
                  </Button>
                </div>
              )}
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default ImageAnalyzer;

