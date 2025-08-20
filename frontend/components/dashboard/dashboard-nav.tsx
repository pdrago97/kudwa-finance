'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Network, 
  Upload, 
  Settings, 
  Users, 
  FileText,
  BarChart3,
  Zap,
  Database
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Overview and metrics'
  },
  {
    name: 'Chat',
    href: '/dashboard/chat',
    icon: MessageSquare,
    description: 'AI assistant and conversations'
  },
  {
    name: 'Knowledge Graph',
    href: '/dashboard/graph',
    icon: Network,
    description: 'Ontology visualization'
  },
  {
    name: 'Canvas',
    href: '/dashboard/canvas',
    icon: BarChart3,
    description: 'Custom dashboard builder'
  },
  {
    name: 'Upload',
    href: '/dashboard/upload',
    icon: Upload,
    description: 'Document processing'
  },
  {
    name: 'Documents',
    href: '/dashboard/documents',
    icon: FileText,
    description: 'File management'
  },
  {
    name: 'Analytics',
    href: '/dashboard/analytics',
    icon: Zap,
    description: 'Advanced insights'
  },
  {
    name: 'Data',
    href: '/dashboard/data',
    icon: Database,
    description: 'Entity and instance management'
  },
]

const adminNavigation = [
  {
    name: 'Admin',
    href: '/admin',
    icon: Settings,
    description: 'System configuration'
  },
  {
    name: 'Users',
    href: '/admin/users',
    icon: Users,
    description: 'User management'
  },
]

export function DashboardNav() {
  const pathname = usePathname()

  return (
    <nav className="w-64 border-r bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="space-y-4 py-4">
        {/* Main Navigation */}
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Platform
          </h2>
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== '/dashboard' && pathname.startsWith(item.href))
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors',
                    isActive 
                      ? 'bg-accent text-accent-foreground' 
                      : 'text-muted-foreground'
                  )}
                >
                  <item.icon className="mr-3 h-4 w-4" />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className="text-xs text-muted-foreground group-hover:text-accent-foreground/70">
                      {item.description}
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Admin Navigation */}
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Administration
          </h2>
          <div className="space-y-1">
            {adminNavigation.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href)
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors',
                    isActive 
                      ? 'bg-accent text-accent-foreground' 
                      : 'text-muted-foreground'
                  )}
                >
                  <item.icon className="mr-3 h-4 w-4" />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className="text-xs text-muted-foreground group-hover:text-accent-foreground/70">
                      {item.description}
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Quick Actions
          </h2>
          <div className="space-y-1">
            <button className="w-full group flex items-center rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <Upload className="mr-3 h-4 w-4" />
              <div className="flex-1 text-left">
                <div>Upload Document</div>
                <div className="text-xs text-muted-foreground group-hover:text-accent-foreground/70">
                  Process new files
                </div>
              </div>
            </button>
            <button className="w-full group flex items-center rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <MessageSquare className="mr-3 h-4 w-4" />
              <div className="flex-1 text-left">
                <div>New Chat</div>
                <div className="text-xs text-muted-foreground group-hover:text-accent-foreground/70">
                  Start conversation
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
