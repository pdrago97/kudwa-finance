import { DashboardNav } from '@/components/dashboard/dashboard-nav'
import { DashboardHeaderSimple } from '@/components/dashboard/dashboard-header-simple'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeaderSimple />
      <div className="flex">
        <DashboardNav />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
