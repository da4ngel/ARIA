import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import App from '@/App'
import '@/styles/index.css'

const container = document.getElementById('root')
if (!container) {
  throw new Error('index.html is missing <div id="root">; the renderer cannot mount.')
}

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
