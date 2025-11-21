import { useState, useEffect } from 'react'
import './App.css'
import { preprocessImage, fileToBase64, downloadImage, checkServerHealth } from './api/imageApi'

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

  // Kiểm tra server khi load trang
  useEffect(() => {
    checkServerHealth().then(setServerOnline)
  }, [])

  // Hàm xử lý file chung (dùng cho cả upload và drag & drop)
  const processImageFile = async (file) => {
    if (!file) return

    // Kiểm tra file là ảnh
    if (!file.type.startsWith('image/')) {
      setError('Vui lòng chọn file ảnh!')
      return
    }

    try {
      setError(null)
      const base64 = await fileToBase64(file)
      setOriginalImage(base64)
      setProcessedImage(null) // Reset ảnh đã xử lý
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

  // Xử lý ảnh
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

  // Download ảnh kết quả
  const handleDownload = () => {
    if (processedImage) {
      const filename = `drawify_${method}_${intensity}_${Date.now()}.png`
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
        <h1><i className="fas fa-palette"></i> Drawify - Image Preprocessing</h1>
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

            <button 
              onClick={handleProcessImage} 
              disabled={loading || !serverOnline}
              className="btn btn-primary"
            >
              {loading ? <><i className="fas fa-spinner fa-spin"></i> Đang xử lý...</> : <><i className="fas fa-play-circle"></i> Xử lý ảnh</>}
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
          </div>
        )}

        {/* Images Display */}
        {originalImage && (
          <section className="images-section">
            <h2><i className="fas fa-images"></i> Bước 3: So sánh kết quả</h2>
            
            <div className="images-container">
              {/* Original Image */}
              <div className="image-box">
                <h3>Ảnh gốc</h3>
                <img src={originalImage} alt="Original" className="image" />
              </div>

              {/* Processed Image */}
              <div className="image-box">
                <h3>Ảnh đã xử lý (Xám + Mịn)</h3>
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
              <li>Chọn phương pháp làm mịn và cường độ</li>
              <li>Nhấn "Xử lý ảnh" để xem kết quả</li>
              <li>So sánh ảnh gốc và ảnh đã xử lý</li>
              <li>Tải ảnh kết quả về máy</li>
            </ol>

            <div className="tech-info">
              <h3><i className="fas fa-microscope"></i> Kỹ thuật sử dụng:</h3>
              <ul>
                <li><strong>Grayscale Conversion</strong>: Chuyển ảnh màu sang xám</li>
                <li><strong>Bilateral Filter</strong>: Làm mịn nhưng giữ biên (edge-preserving)</li>
                <li><strong>Gaussian Blur</strong>: Làm mịn đều toàn bộ</li>
                <li><strong>Median Blur</strong>: Loại bỏ nhiễu muối tiêu</li>
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
