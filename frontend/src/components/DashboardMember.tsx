/**
 * DashboardMember Component
 * Main dashboard for investors showing portfolio overview and project progress
 */

'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, ProgressBar, Badge, Button } from './ui'
import { ProjectCard } from './ProjectCard'
import { AlertSystem } from './AlertSystem'
import { dashboardAPI, projectsAPI, type ProjectProgress } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { formatCurrency, formatPercent } from '@/lib/utils'

interface DashboardStats {
  total_invested: number
  active_investments_count: number
  total_returns: number
  membership_status?: string
}

interface DashboardMemberProps {
  userId?: number
}

export function DashboardMember({ userId }: DashboardMemberProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await dashboardAPI.getDashboard()
      return response.data as DashboardStats & {
        pending_alerts: any[]
        active_projects: ProjectProgress[]
      }
    },
  })

  // Fetch projects
  const { data: projectsData, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects', { status: 'funding' }],
    queryFn: async () => {
      const response = await projectsAPI.list({ status_filter: 'funding', limit: 10 })
      return response.data
    },
  })

  const handleInvest = (projectId: number) => {
    // Navigate to investment page or open modal
    console.log('Invest in project:', projectId)
  }

  if (dashboardLoading || projectsLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-4 bg-secondary rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-secondary rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Seguimiento de tus inversiones y proyectos activos
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Invertido"
          value={formatCurrency(dashboardData?.total_invested || 0)}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Inversiones Activas"
          value={dashboardData?.active_investments_count?.toString() || '0'}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
        <StatCard
          title="Retornos Totales"
          value={formatCurrency(dashboardData?.total_returns || 0)}
          variant="success"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
        <StatCard
          title="Estado Membership"
          value={dashboardData?.membership_status?.toUpperCase() || 'N/A'}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          }
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Alerts Panel */}
        <div className="lg:col-span-1">
          <AlertSystem limit={5} />
        </div>

        {/* Active Projects Progress */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Progreso de Proyectos Activos</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.active_projects && dashboardData.active_projects.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.active_projects.map((project) => (
                    <div key={project.project_id} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{project.title}</span>
                        <span className="text-sm text-muted-foreground">
                          {formatCurrency(project.raised_amount)} / {formatCurrency(project.target_amount)}
                        </span>
                      </div>
                      <ProgressBar value={project.raised_percent} showLabel={false} />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{formatPercent(project.raised_percent)}</span>
                        {project.days_remaining !== null && (
                          <span>{project.days_remaining} días restantes</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No tenés proyectos activos aún</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Available Projects */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Proyectos Disponibles</h2>
          <div className="flex gap-2">
            {['level_1', 'level_2', 'level_3'].map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
              >
                {category === 'level_1' ? 'Cebollitas' : category === 'level_2' ? '1ra Div' : 'Senior'}
              </Button>
            ))}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projectsData?.map((project: any) => (
            <ProjectCard
              key={project.id}
              project={project}
              onInvest={handleInvest}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

interface StatCardProps {
  title: string
  value: string
  icon: React.ReactNode
  variant?: 'default' | 'success'
}

function StatCard({ title, value, icon, variant = 'default' }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <p className={`text-2xl font-bold ${variant === 'success' ? 'text-green-600 dark:text-green-400' : ''}`}>
                {value}
              </p>
            </div>
            <div className="p-3 rounded-full bg-secondary text-secondary-foreground">
              {icon}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
