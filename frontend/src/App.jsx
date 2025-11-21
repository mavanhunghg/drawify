import { useState, useEffect } from 'react'
import './App.css'
import { preprocessImage, fileToBase64, downloadImage, checkServerHealth, sketchImage } from './api/imageApi'

function App() {
  const [originalImage, setOriginalImage] = useState(null)
  const [processedImage, setProcessedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [method, setMethod] = useState('bilateral')
  const [intensity, setIntensity] = useState('medium')
  const [serverOnline, setServerOnline] = useState(false)
  const [processingInfo, setProcessingInfo] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [mode, setMode] = useState('preprocess')
  const [edgeMethod, setEdgeMethod] = useState('canny')
  const [detailLevel, setDetailLevel] = useState('medium')

  // Kiểm tra server khi load trang
  useEffect(() => {
    checkServerHealth().then(setServerOnline)
  }, [])

  // Hàm xử lý file chung (dùng cho cả upload và drag & drop)
  const processImageFile = async (file) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setError('Vui lòng chọn file ảnh!')
      return
    }
    try {
      setError(null)
      const base64 = await fileToBase64(file)
      setOriginalImage(base64)
      setProcessedImage(null)
      setProcessingInfo(null)
    } catch (err) {
      setError('Không thể đọc file ảnh: ' + err.message)
    }
  }

  // Xử lý upload ảnh từ input
  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    await processImageFile(file)
  }

  // Xử lý drag over
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  // Xử lý drag leave
  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  // Xử lý drop
  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      await processImageFile(files[0])
    }
  }

  // Xử lý ảnh preprocess (xám + mịn)
  const handleProcessImage = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: python app.py')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await preprocessImage(originalImage, method, intensity)
      setProcessedImage(result.image)
      setProcessingInfo({
        mode: 'preprocess',
        method: result.method,
        intensity: result.intensity,
        message: result.message,
        shape: result.shape
      })
    } catch (err) {
      setError('Lỗi xử lý ảnh: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Xử lý ảnh Sketch
  const handleSketchImage = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: python app.py')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await sketchImage(originalImage, method, intensity, edgeMethod, detailLevel)
      setProcessedImage(result.image)
      setProcessingInfo({
        mode: 'sketch',
        method,
        intensity,
        edgeMethod,
        detailLevel,
        message: result.message,
        shape: result.shape
      })
    } catch (err) {
      setError('Lỗi xử lý sketch: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Download ảnh kết quả
  const handleDownload = () => {
    if (processedImage) {
      const filename = `drawify_${mode}_${method}_${intensity}_${mode === 'sketch' ? edgeMethod : ''}_${Date.now()}.png`
      downloadImage(processedImage, filename)
    }
  }

  // Reset tất cả
  const handleReset = () => {
    setOriginalImage(null)
    setProcessedImage(null)
    setError(null)
    setProcessingInfo(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1><i className="fas fa-palette"></i> Drawify - Image Preprocessing & Sketch</h1>
        <div className={`server-status ${serverOnline ? 'online' : 'offline'}`}>
          {serverOnline ? <><i className="fas fa-check-circle"></i> Server đang chạy</> : <><i className="fas fa-times-circle"></i> Server offline - Chạy: python app.py</>}
        </div>
      </header>

      <main className="main">
        {/* Upload Section */}
        <section className="upload-section">
          <h2><i className="fas fa-upload"></i> Bước 1: Tải ảnh lên</h2>
          {/* Drag & Drop Zone */}
          <div
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <i className="fas fa-cloud-upload-alt"></i>
            <p>Kéo thả ảnh vào đây</p>
            <p className="or-text">hoặc</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-label">
              Chọn ảnh từ máy
            </label>
          </div>

          {originalImage && (
            <button onClick={handleReset} className="btn btn-secondary" style={{marginTop: '1rem'}}>
              <i className="fas fa-redo"></i> Chọn ảnh khác
            </button>
          )}
        </section>

        {/* Settings Section */}
        {originalImage && (
          <section className="settings-section">
            <h2><i className="fas fa-cog"></i> Bước 2: Cấu hình xử lý</h2>
            
            <div className="setting-group">
              <label>Kiểu xử lý:</label>
              <select value={mode} onChange={e => setMode(e.target.value)}>
                <option value="preprocess">Xám + Mịn</option>
                <option value="sketch">Sketch (Tranh vẽ tay)</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Phương pháp làm mịn:</label>
              <select value={method} onChange={(e) => setMethod(e.target.value)} className="select">
                <option value="bilateral">Bilateral Filter (Khuyên dùng - giữ biên)</option>
                <option value="gaussian">Gaussian Blur (Làm mịn đều)</option>
                <option value="median">Median Blur (Loại nhiễu)</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Cường độ làm mịn:</label>
              <select value={intensity} onChange={(e) => setIntensity(e.target.value)} className="select">
                <option value="light">Nhẹ (Light)</option>
                <option value="medium">Vừa (Medium)</option>
                <option value="strong">Mạnh (Strong)</option>
              </select>
            </div>

            {mode === 'sketch' && (
              <>
                <div className="setting-group">
                  <label>Phương pháp phát hiện biên:</label>
                  <select value={edgeMethod} onChange={e => setEdgeMethod(e.target.value)} className="select">
                    <option value="canny">Canny (Khuyên dùng)</option>
                    <option value="sobel">Sobel</option>
                    <option value="laplacian">Laplacian</option>
                    <option value="log">LoG (Laplacian of Gaussian)</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Mức độ chi tiết:</label>
                  <select value={detailLevel} onChange={e => setDetailLevel(e.target.value)} className="select">
                    <option value="light">Nhẹ (Light) - Nét ít</option>
                    <option value="medium">Vừa (Medium) - Cân bằng</option>
                    <option value="enhanced">Nâng cao (Enhanced) - Nét nhiều</option>
                    <option value="maximum">Cực đại (Maximum) - Nét chi tiết tối đa</option>
                  </select>
                </div>
              </>
            )}

            <button
              onClick={mode === 'sketch' ? handleSketchImage : handleProcessImage}
              disabled={loading || !serverOnline}
              className="btn btn-primary"
            >
              {loading ? <><i className="fas fa-spinner fa-spin"></i> Đang xử lý...</> :
                mode === 'sketch'
                  ? <><i className="fas fa-pencil-alt"></i> Tạo Sketch</>
                  : <><i className="fas fa-play-circle"></i> Xử lý ảnh</>
              }
            </button>
          </section>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i> {error}
          </div>
        )}

        {/* Processing Info */}
        {processingInfo && (
          <div className="info-message">
            <i className="fas fa-check-circle"></i> {processingInfo.message}
            {processingInfo.shape && (
              <span> | Kích thước: {processingInfo.shape.join(' × ')} pixels</span>
            )}
            {processingInfo.mode === 'sketch' && (
              <>
                <span> | Phát hiện biên: {processingInfo.edgeMethod}</span>
                <span> | Chi tiết: {processingInfo.detailLevel}</span>
              </>
            )}
          </div>
        )}

        {/* Images Display */}
        {originalImage && (
          <section className="images-section">
            <h2><i className="fas fa-images"></i> Bước 3: So sánh kết quả</h2>
            <div className="images-container">
              <div className="image-box">
                <h3>Ảnh gốc</h3>
                <img src={originalImage} alt="Original" className="image" />
              </div>
              <div className="image-box">
                <h3>
                  {mode === 'sketch' ? 'Ảnh Sketch (Tranh vẽ tay)' : 'Ảnh đã xử lý (Xám + Mịn)'}
                </h3>
                {processedImage ? (
                  <>
                    <img src={processedImage} alt="Processed" className="image" />
                    <button onClick={handleDownload} className="btn btn-success">
                      <i className="fas fa-download"></i> Tải ảnh về
                    </button>
                  </>
                ) : (
                  <div className="placeholder">
                    <p>Chưa có ảnh xử lý</p>
                    <p><i className="fas fa-arrow-up"></i> Nhấn "Xử lý ảnh" ở trên</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Instructions */}
        {!originalImage && (
          <section className="instructions">
            <h2><i className="fas fa-book"></i> Hướng dẫn sử dụng</h2>
            <ol>
              <li>Đảm bảo backend server đang chạy: <code>python app.py</code></li>
              <li>Tải ảnh lên (ảnh y tế, ảnh tự nhiên, ảnh công nghiệp...)</li>
              <li>Chọn kiểu xử lý, phương pháp làm mịn và cường độ</li>
              <li>Nếu muốn chuyển sang sketch, chọn phương pháp phát hiện biên và mức độ chi tiết</li>
              <li>Nhấn "Xử lý ảnh" hoặc "Tạo Sketch" để xem kết quả</li>
              <li>So sánh ảnh gốc và ảnh đã xử lý/sketch</li>
              <li>Tải ảnh kết quả về máy</li>
            </ol>
            <div className="tech-info">
              <h3><i className="fas fa-microscope"></i> Kỹ thuật sử dụng:</h3>
              <ul>
                <li><strong>Grayscale Conversion</strong>: Chuyển ảnh màu sang xám</li>
                <li><strong>Bilateral Filter</strong>: Làm mịn nhưng giữ biên (edge-preserving)</li>
                <li><strong>Gaussian Blur</strong>: Làm mịn đều toàn bộ</li>
                <li><strong>Median Blur</strong>: Loại bỏ nhiễu muối tiêu</li>
                <li><strong>Edge Detection</strong>: Phát hiện biên (Canny, Sobel, Laplacian, LoG) cho sketch</li>
                <li><strong>CLAHE</strong>: Tăng tương phản thích ứng để tăng nét chi tiết</li>
              </ul>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Chuyển ảnh thành tranh vẽ </p>
      </footer>
    </div>
  )
}

export default App
