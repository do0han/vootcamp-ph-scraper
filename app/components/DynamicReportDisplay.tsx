'use client'

import dynamic from 'next/dynamic'
import { LoadingState } from './LoadingState'

// Dynamically import ReportDisplay to reduce initial bundle size
export const DynamicReportDisplay = dynamic(
  () => import('./ReportDisplay').then(mod => ({ default: mod.ReportDisplay })),
  {
    loading: () => <LoadingState />,
    ssr: false
  }
)