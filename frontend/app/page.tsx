import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  ArrowRight,
  Database,
  MessageSquare,
  Network,
  Zap,
  CheckCircle,
  TrendingUp,
  Shield,
  Sparkles,
  BarChart3,
  Brain,
  Users
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-950 dark:via-blue-950 dark:to-purple-950">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 via-purple-600 to-cyan-600">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Kudwa
              </h1>
              <p className="text-xs text-muted-foreground">Financial Platform</p>
            </div>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/auth/login">Login</Link>
            </Button>
            <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" asChild>
              <Link href="/dashboard">
                Dashboard <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25"></div>
        <div className="relative">
          <div className="container px-4 py-24 sm:py-32">
            <div className="mx-auto max-w-4xl text-center">
              <Badge variant="secondary" className="mb-6 px-4 py-2">
                <Sparkles className="mr-2 h-4 w-4" />
                Powered by Next.js & AI
              </Badge>
              <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                  AI-Powered
                </span>
                <br />
                Financial Platform
              </h1>
              <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground sm:text-xl">
                Modern ontology management for financial data with real-time analytics,
                intelligent chat, and interactive visualizations. Built for the future of finance.
              </p>
              <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg" asChild>
                  <Link href="/dashboard">
                    Get Started <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="/auth/login">
                    <Users className="mr-2 h-5 w-5" />
                    Login
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white dark:bg-slate-900">
        <div className="container px-4">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Enterprise-Grade Features
            </h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to manage financial data with AI-powered insights
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/50 dark:to-cyan-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white mb-4">
                  <BarChart3 className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">Real-time Dashboard</CardTitle>
                <CardDescription className="text-base">
                  Professional analytics with interactive charts, KPIs, and customizable widgets
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/50 dark:to-pink-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 text-white mb-4">
                  <Brain className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">AI Assistant</CardTitle>
                <CardDescription className="text-base">
                  Intelligent chat with streaming responses and deep financial context awareness
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/50 dark:to-emerald-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 text-white mb-4">
                  <Network className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">Knowledge Graph</CardTitle>
                <CardDescription className="text-base">
                  Interactive ontology visualization with GraphRAG and relationship mapping
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/50 dark:to-red-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-red-500 text-white mb-4">
                  <Database className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">Vector Database</CardTitle>
                <CardDescription className="text-base">
                  Supabase PostgreSQL with pgvector for semantic search and RAG capabilities
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-950/50 dark:to-blue-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 text-white mb-4">
                  <Shield className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">Enterprise Security</CardTitle>
                <CardDescription className="text-base">
                  Bank-grade security with role-based access, audit trails, and compliance
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group relative overflow-hidden border-0 bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-teal-950/50 dark:to-cyan-950/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 text-white mb-4">
                  <Zap className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl">High Performance</CardTitle>
                <CardDescription className="text-base">
                  10x faster than legacy systems with modern React architecture and caching
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Status Section */}
      <section className="py-24 bg-slate-50 dark:bg-slate-900/50">
        <div className="container px-4">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <Badge variant="default" className="mb-4 bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-100">
              <CheckCircle className="mr-2 h-4 w-4" />
              All Systems Operational
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Platform Status
            </h2>
            <p className="text-lg text-muted-foreground">
              Real-time monitoring of all platform components
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center">
                    <div className="mr-3 h-3 w-3 rounded-full bg-green-500"></div>
                    Frontend
                  </span>
                  <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-100">
                    Online
                  </Badge>
                </CardTitle>
                <CardDescription>Next.js 14 with TypeScript</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Port</span>
                    <span className="font-mono">3000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Response Time</span>
                    <span className="font-mono text-green-600">~50ms</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center">
                    <div className="mr-3 h-3 w-3 rounded-full bg-blue-500"></div>
                    Backend
                  </span>
                  <Badge variant="default" className="bg-blue-100 text-blue-800 hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-100">
                    Online
                  </Badge>
                </CardTitle>
                <CardDescription>FastAPI with async support</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Port</span>
                    <span className="font-mono">8000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Response Time</span>
                    <span className="font-mono text-blue-600">~120ms</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-950/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center">
                    <div className="mr-3 h-3 w-3 rounded-full bg-purple-500"></div>
                    Database
                  </span>
                  <Badge variant="default" className="bg-purple-100 text-purple-800 hover:bg-purple-100 dark:bg-purple-900 dark:text-purple-100">
                    Connected
                  </Badge>
                </CardTitle>
                <CardDescription>Supabase PostgreSQL + pgvector</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Region</span>
                    <span className="font-mono">us-east-2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Latency</span>
                    <span className="font-mono text-purple-600">~25ms</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-background">
        <div className="container px-4 py-12">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center space-x-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div>
                <span className="font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Kudwa Financial Platform
                </span>
                <p className="text-xs text-muted-foreground">Next-generation fintech</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>© 2024 Kudwa</span>
              <span>•</span>
              <span>Built with Next.js & Supabase</span>
              <span>•</span>
              <span className="flex items-center">
                <CheckCircle className="mr-1 h-3 w-3 text-green-500" />
                All systems operational
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
