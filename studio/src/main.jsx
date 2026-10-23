// Hands your studio to the framework, which routes the operator's board and each
// graphic.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Studio } from '@single-studio/core'

import { studio } from './studio/studio'
import './css/index.css'

createRoot(document.getElementById('app')).render(
  <StrictMode>
    <Studio studio={studio} />
  </StrictMode>,
)
