import React, { useState, useEffect } from 'react';
import { Upload, message, Progress, Tag, Space, Button, Tooltip, Badge } from 'antd';
import {
  FileOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  ExclamationCircleOutlined,
  PaperClipOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import './FileUpload.css';

// 支持的文件类型
const SUPPORTED_FORMATS = [
  '.pdf',
  '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
  '.pptx', '.ppt',
  '.docx', '.doc',
  '.xlsx', '.xls',
  '.html', '.htm',
  '.epub'
];

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
const MAX_FILE_COUNT = 10;

const FileUpload = ({ onFilesChange, onParsingComplete, onParsingStart, disabled }) => {
  const [fileList, setFileList] = useState([]);
  const [parsedFiles, setParsedFiles] = useState([]);
  const [showFileList, setShowFileList] = useState(false);

  // 检查文件类型
  const checkFileType = (file) => {
    const fileName = file.name.toLowerCase();
    const isSupported = SUPPORTED_FORMATS.some(format => fileName.endsWith(format));
    if (!isSupported) {
      message.error(`不支持的文件格式: ${file.name}`);
    }
    return isSupported;
  };

  // 检查文件大小
  const checkFileSize = (file) => {
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件 ${file.name} 超过 100MB 限制`);
      return false;
    }
    return true;
  };

  // 文件上传前的检查
  const beforeUpload = (file, fileList) => {
    // 检查文件数量
    if (fileList.length > MAX_FILE_COUNT) {
      message.error(`最多只能上传 ${MAX_FILE_COUNT} 个文件`);
      return Upload.LIST_IGNORE;
    }

    // 检查文件类型
    if (!checkFileType(file)) {
      return Upload.LIST_IGNORE;
    }

    // 检查文件大小
    if (!checkFileSize(file)) {
      return Upload.LIST_IGNORE;
    }

    return false; // 阻止自动上传
  };

  // 文件列表变化 - 自动解析
  const handleChange = async ({ fileList: newFileList }) => {
    setFileList(newFileList);
    onFilesChange?.(newFileList);

    // 自动解析新上传的文件
    if (newFileList.length > fileList.length) {
      // 有新文件上传，自动解析
      const newFiles = newFileList.filter(
        newFile => !fileList.some(oldFile => oldFile.uid === newFile.uid)
      );

      if (newFiles.length > 0) {
        // 延迟一下，确保文件列表更新完成
        setTimeout(() => {
          parseFiles(newFiles);
        }, 100);
      }
    }
  };

  // 移除文件
  const handleRemove = (file) => {
    const newFileList = fileList.filter(f => f.uid !== file.uid);
    setFileList(newFileList);

    // 同时移除已解析的文件
    const newParsedFiles = parsedFiles.filter(f => f.uid !== file.uid);
    setParsedFiles(newParsedFiles);

    onFilesChange?.(newFileList);

    // 如果没有文件了，关闭文件列表
    if (newFileList.length === 0) {
      setShowFileList(false);
    }
  };

  // 解析指定的文件
  const parseFiles = async (filesToParse) => {
    if (filesToParse.length === 0) {
      return;
    }

    // 标记这些文件为解析中
    const parsingFiles = filesToParse.map(f => ({
      uid: f.uid,
      name: f.name,
      success: false,
      parsing: true,
      error: null,
    }));

    setParsedFiles(prev => {
      // 移除旧的解析记录，添加新的解析中状态
      const filtered = prev.filter(p => !filesToParse.some(f => f.uid === p.uid));
      return [...filtered, ...parsingFiles];
    });

    onParsingStart?.(); // 通知父组件开始解析
    const formData = new FormData();

    filesToParse.forEach(file => {
      formData.append('files', file.originFileObj);
    });

    formData.append('max_concurrent', '3');
    formData.append('output_format', 'markdown');

    try {
      const response = await fetch('http://localhost:8000/api/convert/markdown/batch', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '解析失败');
      }

      const result = await response.json();

      // 处理解析结果
      const parsed = result.results.map((r, index) => ({
        uid: filesToParse[index].uid,
        name: r.filename || filesToParse[index].name,
        success: r.success,
        file_id: r.file_id || null,
        parsing: false,
        error: r.message,
      }));

      setParsedFiles(prev => {
        // 更新解析结果
        const filtered = prev.filter(p => !filesToParse.some(f => f.uid === p.uid));
        return [...filtered, ...parsed];
      });

      const successCount = result.success_count;
      const failedCount = result.failed_count;

      if (successCount > 0) {
        message.success(`成功解析 ${successCount} 个文件${failedCount > 0 ? `，${failedCount} 个失败` : ''}`);
      } else {
        message.error('所有文件解析失败');
      }

      // 通知父组件解析完成
      onParsingComplete?.(parsed);

    } catch (error) {
      console.error('解析文件失败:', error);
      message.error(`解析失败: ${error.message}`);

      // 标记为解析失败
      setParsedFiles(prev => {
        const filtered = prev.filter(p => !filesToParse.some(f => f.uid === p.uid));
        const failed = filesToParse.map(f => ({
          uid: f.uid,
          name: f.name,
          success: false,
          parsing: false,
          error: error.message,
        }));
        return [...filtered, ...failed];
      });
    }
  };

  // 获取文件状态图标
  const getFileStatusIcon = (file) => {
    const parsedFile = parsedFiles.find(f => f.uid === file.uid);

    if (parsedFile?.parsing) {
      return <LoadingOutlined style={{ color: '#1890ff' }} spin />;
    }

    if (parsedFile) {
      if (parsedFile.success) {
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      } else {
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      }
    }

    return <FileOutlined />;
  };

  // 检查是否有文件正在解析
  const isParsing = parsedFiles.some(f => f.parsing);

  // 检查是否所有文件都已解析完成
  const allFilesParsed = fileList.length > 0 && fileList.every(file => {
    const parsedFile = parsedFiles.find(f => f.uid === file.uid);
    return parsedFile && !parsedFile.parsing;
  });

  // 通知父组件解析状态
  useEffect(() => {
    if (allFilesParsed) {
      const successfulFiles = parsedFiles.filter(f => f.success);
      onParsingComplete?.(successfulFiles);
    }
  }, [allFilesParsed, parsedFiles]);

  // 获取文件大小显示
  const getFileSizeText = (size) => {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else {
      return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    fileList,
    beforeUpload,
    onChange: handleChange,
    onRemove: handleRemove,
    showUploadList: false,
    disabled: disabled,
  };

  // 计算未解析完成的文件数
  const parsingCount = parsedFiles.filter(f => f.parsing).length;
  const totalFiles = fileList.length;
  const parsedCount = parsedFiles.filter(f => !f.parsing).length;

  return (
    <div className="file-upload-container-compact">
      {/* 紧凑的上传按钮 */}
      <div className="upload-button-wrapper">
        <Upload {...uploadProps}>
          <Button
            icon={<PaperClipOutlined />}
            disabled={disabled}
            type="text"
          >
            添加文件
          </Button>
        </Upload>

        {/* 文件状态指示器 */}
        {fileList.length > 0 && (
          <Space size="small">
            <Badge
              count={totalFiles}
              showZero
              style={{ backgroundColor: '#1890ff' }}
            />
            {isParsing && (
              <Tag icon={<LoadingOutlined spin />} color="processing">
                解析中 {parsingCount}/{totalFiles}
              </Tag>
            )}
            {allFilesParsed && (
              <Tag icon={<CheckCircleOutlined />} color="success">
                已完成 {parsedCount}/{totalFiles}
              </Tag>
            )}
            <Button
              type="text"
              size="small"
              icon={showFileList ? <CloseOutlined /> : <FileOutlined />}
              onClick={() => setShowFileList(!showFileList)}
            >
              {showFileList ? '隐藏' : '查看'}
            </Button>
          </Space>
        )}
      </div>

      {/* 可折叠的文件列表 */}
      <AnimatePresence>
        {showFileList && fileList.length > 0 && (
          <motion.div
            className="file-list-compact"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {fileList.map((file) => {
              const parsedFile = parsedFiles.find(f => f.uid === file.uid);

              return (
                <motion.div
                  key={file.uid}
                  className="file-item-compact"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <div className="file-info">
                    <div className="file-icon">
                      {getFileStatusIcon(file)}
                    </div>
                    <div className="file-details">
                      <div className="file-name">
                        <Tooltip title={file.name}>
                          {file.name}
                        </Tooltip>
                      </div>
                      <div className="file-meta">
                        <span className="file-size">
                          {getFileSizeText(file.size)}
                        </span>
                        {parsedFile && !parsedFile.parsing && (
                          <Tag
                            color={parsedFile.success ? 'success' : 'error'}
                            style={{ marginLeft: 8 }}
                          >
                            {parsedFile.success ? '✓' : '✗'}
                          </Tag>
                        )}
                      </div>
                      {parsedFile && !parsedFile.success && !parsedFile.parsing && (
                        <div className="file-error">
                          {parsedFile.error}
                        </div>
                      )}
                    </div>
                  </div>
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemove(file)}
                    disabled={parsedFile?.parsing}
                  />
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;

