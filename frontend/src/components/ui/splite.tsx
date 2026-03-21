import { Suspense, lazy, Component, type ReactNode } from 'react'
const Spline = lazy(() => import('@splinetool/react-spline'))

class SplineErrorBoundary extends Component<{children: ReactNode, fallback: ReactNode}, {hasError: boolean}> {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  render() { return this.state.hasError ? this.props.fallback : this.props.children }
}

interface SplineSceneProps { scene: string; className?: string }

const SplineFallback = () => (
  <div className="w-full h-full flex items-center justify-center flex-col gap-4 bg-gradient-to-br from-indigo-950/30 to-black rounded-2xl">
    <svg width="80" height="80" viewBox="0 0 36 44" fill="none" className="animate-pulse">
      <path d="M23.5 5.7 16.2.4a2.1 2.1 0 0 0-2.4 0L.4 10a2 2 0 0 0-.4 1.2v21.6c0 .5.2.9.4 1.2l13.4 9.6a2.1 2.1 0 0 0 2.4 0L29.6 34a2 2 0 0 0 .4-1.2V11.2a2 2 0 0 0-.4-1.2L23.5 5.7Z" fill="#4da2ff"/>
    </svg>
    <p className="text-neutral-400 text-sm">Sui DeFi Jarvis</p>
  </div>
)

export function SplineScene({ scene, className }: SplineSceneProps) {
  return (
    <SplineErrorBoundary fallback={<SplineFallback />}>
      <Suspense fallback={<SplineFallback />}>
        <Spline scene={scene} className={className} />
      </Suspense>
    </SplineErrorBoundary>
  )
}
