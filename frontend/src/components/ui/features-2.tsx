import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { type ReactNode } from 'react'

interface Feature2Item { icon: ReactNode; title: string; description: string }

export function Features2({ title, subtitle, features }: { title: string; subtitle: string; features: Feature2Item[] }) {
  return (
    <section className="py-16 md:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <div className="text-center">
          <h2 className="text-balance text-4xl font-semibold lg:text-5xl">{title}</h2>
          <p className="mt-4 text-neutral-400">{subtitle}</p>
        </div>
        <div className="mx-auto mt-8 grid max-w-sm gap-6 md:mt-16 md:max-w-full md:grid-cols-3 *:text-center">
          {features.map((f, i) => (
            <Card key={i} className="group border-0 bg-neutral-900 shadow-none">
              <CardHeader className="pb-3">
                <CardDecorator>{f.icon}</CardDecorator>
                <h3 className="mt-6 font-medium text-white">{f.title}</h3>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-neutral-400">{f.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

const CardDecorator = ({ children }: { children: ReactNode }) => (
  <div className="relative mx-auto size-36 [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)]">
    <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:24px_24px]" />
    <div className="bg-neutral-950 absolute inset-0 m-auto flex size-12 items-center justify-center border-t border-l border-neutral-800">{children}</div>
  </div>
)
