'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { formatRelativeTime } from '@/lib/utils'
import { 
  FileText, 
  MessageSquare, 
  Database, 
  Upload,
  Network,
  User
} from 'lucide-react'

interface Activity {
  id: string
  type: string
  title: string
  description: string
  timestamp: Date
  user: string
}

interface RecentActivityProps {
  activities: Activity[]
  isLoading?: boolean
}

const activityIcons = {
  document_uploaded: FileText,
  chat_session: MessageSquare,
  entity_created: Database,
  file_processed: Upload,
  relation_added: Network,
  user_action: User,
}

const activityColors = {
  document_uploaded: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  chat_session: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  entity_created: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  file_processed: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  relation_added: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
  user_action: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
}

export function RecentActivity({ activities, isLoading = false }: RecentActivityProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest system events and user actions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-start space-x-3">
              <Skeleton className="h-8 w-8 rounded-full" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
                <Skeleton className="h-3 w-1/4" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest system events and user actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No recent activity to display</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest system events and user actions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const Icon = activityIcons[activity.type as keyof typeof activityIcons] || User
            const colorClass = activityColors[activity.type as keyof typeof activityColors] || activityColors.user_action

            return (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                <div className={`p-2 rounded-full ${colorClass}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium truncate">
                      {activity.title}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {formatRelativeTime(activity.timestamp)}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {activity.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    by {activity.user}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
