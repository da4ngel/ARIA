import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { OverlayApp } from '@/overlay/OverlayApp'
import '@/styles/index.css'

const container = document.getElementById('overlay')
if (!container) {
  throw new Error('overlay.html is missing <div id="overlay">; the overlay cannot mount.')
}

createRoot(container).render(
  <StrictMode>
    <OverlayApp />
  </StrictMode>,
)
