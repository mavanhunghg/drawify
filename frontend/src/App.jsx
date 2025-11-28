import { useState, useEffect } from 'react'
import './App.css'
import { preprocessImage, fileToBase64, downloadImage, checkServerHealth, grayscaleOnly, sketchImage, fullPipeline } from './api/imageApi'

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
  const [mode, setMode] = useState('preprocess') // preprocess, grayscale, hoặc sketch
  const [edgeMethod, setEdgeMethod] = useState('canny')
  const [detailLevel, setDetailLevel] = useState('medium')

  // Kiểm tra server khi load trang
  useEffect(() => {
    checkServerHealth().then(setServerOnline)
    const interval = setInterval(() => {
      checkServerHealth().then(setServerOnline)
    }, 5000) // Check mỗi 5 giây
    return () => clearInterval(interval)
  }, [])

  // Hàm xử lý file
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

  // Xử lý upload ảnh
  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    await processImageFile(file)
  }

  // Xử lý drag & drop
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      await processImageFile(files[0])
    }
  }

  // Xử lý Preprocessing (Grayscale + Smoothing)
  const handlePreprocess = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: cd backend && python app.py')
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

  // Xử lý chỉ Grayscale (test)
  const handleGrayscale = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy!')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await grayscaleOnly(originalImage)
      setProcessedImage(result.image)
      setProcessingInfo({
        method: 'grayscale',
        message: result.message,
        shape: result.shape
      })
    } catch (err) {
      setError('Lỗi chuyển xám: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Xử lý Full Pipeline (Hiến + Hùng)
  const handleFullPipeline = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: cd backend && python app.py')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await fullPipeline(
        originalImage,
        method,  // smoothing_method
        intensity,
        edgeMethod,
        detailLevel
      )
      setProcessedImage(result.image)
      setProcessingInfo({
        method: 'full-pipeline',
        smoothing_method: method,
        intensity: intensity,
        edge_method: edgeMethod,
        detail_level: detailLevel,
        message: result.message,
        shape: result.shape,
        steps: result.steps,
        pipeline: result.pipeline
      })
    } catch (err) {
      setError('Lỗi xử lý pipeline: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Xử lý Sketch (Hùng - Edge Detection)
  const handleSketch = async () => {
    if (!originalImage) {
      setError('Vui lòng tải ảnh lên trước!')
      return
    }
    if (!serverOnline) {
      setError('Backend server chưa chạy! Vui lòng chạy: cd backend && python app.py')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await sketchImage(
        originalImage,
        method,  // smoothing_method
        intensity,
        edgeMethod,
        detailLevel
      )
      setProcessedImage(result.image)
      setProcessingInfo({
        method: 'sketch',
        smoothing_method: method,
        intensity: intensity,
        edge_method: edgeMethod,
        detail_level: detailLevel,
        message: result.message,
        shape: result.shape
      })
    } catch (err) {
      setError('Lỗi tạo sketch: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  // Download ảnh
  const handleDownload = () => {
    if (processedImage) {
      const filename = `preprocessed_${method}_${intensity}_${Date.now()}.png`
      downloadImage(processedImage, filename)
    }
  }

  // Reset
  const handleReset = () => {
    setOriginalImage(null)
    setProcessedImage(null)
    setError(null)
    setProcessingInfo(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎨 Drawify - Preprocessing (Hiến)</h1>
        <div className={`server-status ${serverOnline ? 'online' : 'offline'}`}>
          {serverOnline ? (
            <>✅ Server đang chạy</>
          ) : (
            <>❌ Server offline - Chạy: cd backend && python app.py</>
          )}
        </div>
      </header>

      <main className="main">
        {/* Upload Section */}
        <section className="upload-section">
          <h2>📤 Bước 1: Tải ảnh lên</h2>
          <div
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <p>📁 Kéo thả ảnh vào đây</p>
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
              🔄 Chọn ảnh khác
            </button>
          )}
        </section>

        {/* Settings Section */}
        {originalImage && (
          <section className="settings-section">
            <h2>⚙️ Bước 2: Cấu hình xử lý</h2>
            
            <div className="setting-group">
              <label>Chế độ xử lý:</label>
              <select value={mode} onChange={e => setMode(e.target.value)}>
                <option value="full">⭐ Pipeline đầy đủ (Hiến + Hùng) - KHUYÊN DÙNG</option>
                <option value="preprocess">Grayscale + Smoothing (Hiến)</option>
                <option value="grayscale">Chỉ Grayscale (Test)</option>
                <option value="sketch">Edge Detection + Sketch (Hùng)</option>
              </select>
            </div>

            {(mode === 'preprocess' || mode === 'full') && (
              <>
                <div className="setting-group">
                  <label>Phương pháp làm mịn (Hiến):</label>
                  <select value={method} onChange={(e) => setMethod(e.target.value)}>
                    <option value="bilateral">⭐ Bilateral Filter (Giữ biên - Khuyên dùng)</option>
                    <option value="gaussian">Gaussian Blur (Làm mịn đều)</option>
                    <option value="median">Median Blur (Loại nhiễu)</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Cường độ làm mịn (Hiến):</label>
                  <select value={intensity} onChange={(e) => setIntensity(e.target.value)}>
                    <option value="light">Nhẹ (Light) ⭐ - Giữ chi tiết</option>
                    <option value="medium">Vừa (Medium)</option>
                    <option value="strong">Mạnh (Strong)</option>
                  </select>
                </div>
              </>
            )}

            {mode === 'preprocess' && (
              <button
                onClick={handlePreprocess}
                disabled={loading || !serverOnline}
                className="btn btn-primary"
              >
                {loading ? <>⏳ Đang xử lý...</> : <>🚀 Xử lý ảnh (Grayscale + Smoothing)</>}
              </button>
            )}

            {mode === 'grayscale' && (
              <button
                onClick={handleGrayscale}
                disabled={loading || !serverOnline}
                className="btn btn-primary"
              >
                {loading ? <>⏳ Đang xử lý...</> : <>🖼️ Chỉ chuyển Grayscale</>}
              </button>
            )}

            {(mode === 'sketch' || mode === 'full') && (
              <>
                <div className="setting-group">
                  <label>Phương pháp phát hiện biên (Hùng):</label>
                  <select value={edgeMethod} onChange={e => setEdgeMethod(e.target.value)}>
                    <option value="canny">⭐ Canny (Khuyên dùng - Tối ưu nhất)</option>
                    <option value="sobel">Sobel (Gradient - Nhanh)</option>
                    <option value="laplacian">Laplacian (Đạo hàm bậc 2)</option>
                    <option value="log">LoG (Laplacian of Gaussian)</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Mức độ chi tiết Sketch (Hùng):</label>
                  <select value={detailLevel} onChange={e => setDetailLevel(e.target.value)}>
                    <option value="pencil">⭐ Tranh vẽ chì (Pencil) - TỐT NHẤT</option>
                    <option value="natural">Tự nhiên (Natural) - Có shading</option>
                    <option value="medium">Vừa (Medium) - Có shading nhẹ</option>
                    <option value="enhanced">Nâng cao (Enhanced) - Chi tiết cao</option>
                  </select>
                </div>
              </>
            )}

            {mode === 'sketch' && (
              <button
                onClick={handleSketch}
                disabled={loading || !serverOnline}
                className="btn btn-primary"
              >
                {loading ? <>⏳ Đang xử lý...</> : <>🎨 Tạo Sketch (Edge Detection)</>}
              </button>
            )}

            {mode === 'full' && (
              <button
                onClick={handleFullPipeline}
                disabled={loading || !serverOnline}
                className="btn btn-primary"
                style={{fontSize: '1.1rem', padding: '1rem 2rem'}}
              >
                {loading ? (
                  <>⏳ Đang xử lý Pipeline đầy đủ...</>
                ) : (
                  <>🎨🚀 Pipeline đầy đủ: Hiến (Preprocessing) → Hùng (Sketch)</>
                )}
              </button>
            )}
          </section>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Processing Info */}
        {processingInfo && (
          <div className="info-message">
            ✅ {processingInfo.message}
            {processingInfo.shape && (
              <span> | Kích thước: {processingInfo.shape.join(' × ')} pixels</span>
            )}
            {processingInfo.method && processingInfo.method !== 'grayscale' && processingInfo.method !== 'sketch' && (
              <span> | Method: {processingInfo.method} | Intensity: {processingInfo.intensity}</span>
            )}
            {processingInfo.method === 'sketch' && (
              <span> | Edge: {processingInfo.edge_method} | Detail: {processingInfo.detail_level}</span>
            )}
            {processingInfo.method === 'full-pipeline' && (
              <>
                <span> | Smoothing: {processingInfo.smoothing_method} ({processingInfo.intensity})</span>
                <span> | Edge: {processingInfo.edge_method} | Detail: {processingInfo.detail_level}</span>
                {processingInfo.pipeline && (
                  <div style={{marginTop: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)'}}>
                    📋 Pipeline: {processingInfo.pipeline.preprocessing.grayscale} → {processingInfo.pipeline.preprocessing.smoothing} → {processingInfo.pipeline.sketch.edge_detection} → {processingInfo.pipeline.sketch.sketch_effect}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Images Display */}
        {originalImage && (
          <section className="images-section">
            <h2>📊 Bước 3: So sánh kết quả</h2>
            <div className="images-container">
              <div className="image-box">
                <h3>Ảnh gốc</h3>
                <img src={originalImage} alt="Original" className="image" />
              </div>
              <div className="image-box">
                <h3>
                  {mode === 'grayscale' 
                    ? 'Ảnh Grayscale'
                    : mode === 'sketch'
                    ? 'Ảnh Sketch (Edge Detection)'
                    : mode === 'full'
                    ? 'Ảnh Sketch cuối cùng (Pipeline đầy đủ)'
                    : 'Ảnh đã xử lý (Grayscale + Smoothing)'}
                </h3>
                {processedImage ? (
                  <>
                    <img src={processedImage} alt="Processed" className="image" />
                    <button onClick={handleDownload} className="btn btn-success">
                      💾 Tải ảnh về
                    </button>
                  </>
                ) : (
                  <div className="placeholder">
                    <p>Chưa có ảnh xử lý</p>
                    <p>⬆️ Nhấn nút xử lý ở trên</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Instructions */}
        {!originalImage && (
          <section className="instructions">
            <h2>📖 Hướng dẫn sử dụng</h2>
            <ol>
              <li>Đảm bảo backend server đang chạy: <code>cd backend && python app.py</code></li>
              <li>Tải ảnh lên (ảnh y tế, ảnh tự nhiên, ảnh công nghiệp...)</li>
              <li>Chọn phương pháp làm mịn và cường độ</li>
              <li>Nhấn "Xử lý ảnh" để xem kết quả</li>
              <li>So sánh ảnh gốc và ảnh đã xử lý</li>
              <li>Tải ảnh kết quả về máy</li>
            </ol>
            <div className="tech-info">
              <h3>🔬 Kỹ thuật sử dụng (Hiến - Preprocessing):</h3>
              <ul>
                <li><strong>Grayscale Conversion</strong>: Chuyển ảnh màu sang xám (0.299*R + 0.587*G + 0.114*B)</li>
                <li><strong>Bilateral Filter</strong>: Làm mịn nhưng giữ biên (edge-preserving) ⭐</li>
                <li><strong>Gaussian Blur</strong>: Làm mịn đều toàn bộ ảnh</li>
                <li><strong>Median Blur</strong>: Loại bỏ nhiễu muối tiêu</li>
              </ul>
              <h3 style={{marginTop: '1.5rem', color: 'rgba(255,255,255,0.9)'}}>🔬 Kỹ thuật của Hùng (Edge Detection + Sketch):</h3>
              <ul>
                <li><strong>Canny Edge Detection</strong>: Phát hiện biên tối ưu (Gaussian + Gradient + Non-max suppression + Hysteresis) ⭐</li>
                <li><strong>Sobel Operator</strong>: Gradient bậc 1 (nhanh, đơn giản)</li>
                <li><strong>Laplacian</strong>: Đạo hàm bậc 2 (phát hiện biên mảnh)</li>
                <li><strong>LoG</strong>: Laplacian of Gaussian (cân bằng tốt)</li>
                <li><strong>Otsu Thresholding</strong>: Tự động tính ngưỡng tối ưu</li>
              </ul>
              <p><strong>Lưu ý:</strong> Tất cả code được implement thủ công, không dùng OpenCV!</p>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Drawify - Preprocessing Module (Hiến) | Code thủ công - Không dùng OpenCV</p>
      </footer>
    </div>
  )
}

export default App
