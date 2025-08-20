'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { 
  Upload, 
  MessageSquare, 
  Plus, 
  BarChart3,
  FileText,
  Database
} from 'lucide-react'

export function QuickActions() {
  const router = useRouter()
  const { toast } = useToast()
  const [loading, setLoading] = useState<string | null>(null)

  const handleAction = async (action: string, path: string) => {
    setLoading(action)
    
    // Simulate loading for better UX
    await new Promise(resolve => setTimeout(resolve, 500))
    
    try {
      router.push(path)
      toast({
        title: 'Navigation',
        description: `Navigating to ${action}...`,
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to navigate. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setLoading(null)
    }
  }

  const actions = [
    {
      id: 'upload',
      title: 'Upload Document',
      description: 'Process new files',
      icon: Upload,
      path: '/dashboard/upload',
      variant: 'kudwa' as const
    },
    {
      id: 'chat',
      title: 'Start Chat',
      description: 'Ask AI assistant',
      icon: MessageSquare,
      path: '/dashboard/chat',
      variant: 'default' as const
    },
    {
      id: 'canvas',
      title: 'Create Widget',
      description: 'Build dashboard',
      icon: BarChart3,
      path: '/dashboard/canvas',
      variant: 'secondary' as const
    },
    {
      id: 'entity',
      title: 'Add Entity',
      description: 'Extend ontology',
      icon: Database,
      path: '/dashboard/data',
      variant: 'outline' as const
    }
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Quick Actions
        </CardTitle>
        <CardDescription>
          Common tasks and shortcuts
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action) => (
          <Button
            key={action.id}
            variant={action.variant}
            className="w-full justify-start h-auto p-3"
            onClick={() => handleAction(action.title, action.path)}
            disabled={loading === action.id}
          >
            <action.icon className="h-4 w-4 mr-3" />
            <div className="text-left">
              <div className="font-medium">{action.title}</div>
              <div className="text-xs opacity-70">{action.description}</div>
            </div>
          </Button>
        ))}
      </CardContent>
    </Card>
  )
}
