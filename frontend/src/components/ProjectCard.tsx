/**
 * ProjectCard Component
 * Displays project information with funding progress and Club contribution rule
 */

'use client'

import { Card, CardContent, CardHeader, CardTitle, ProgressBar, Badge, Button } from './ui'
import { formatCurrency, formatPercent, getDaysRemaining } from '@/lib/utils'
import { motion } from 'framer-motion'

interface Project {
  id: number
  title: string
  description: string
  short_description?: string
  category: 'level_1' | 'level_2' | 'level_3'
  target_amount: number
  minimum_investment: number
  raised_amount: number
  raised_percent: number
  investor_count: number
  club_contribution_percent?: number
  club_contribution_amount?: number
  club_contribution_triggered: boolean
  status: 'draft' | 'funding' | 'funded' | 'active' | 'completed' | 'cancelled'
  funding_deadline?: string
  expected_return_percent?: number
  expected_duration_months?: number
  risk_rating?: number
}

interface ProjectCardProps {
  project: Project
  onInvest?: (projectId: number) => void
}

export function ProjectCard({ project, onInvest }: ProjectCardProps) {
  const daysRemaining = project.funding_deadline ? getDaysRemaining(project.funding_deadline) : null
  const clubRule = getClubRule(project.category)
  
  const statusColors = {
    draft: 'default',
    funding: 'success',
    funded: 'warning',
    active: 'success',
    completed: 'default',
    cancelled: 'error',
  } as const

  const categoryLabels = {
    level_1: 'Cebollitas',
    level_2: '1ra Div',
    level_3: 'Senior',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={statusColors[project.status] as any}>
                  {project.status.toUpperCase()}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {categoryLabels[project.category]}
                </Badge>
              </div>
              <CardTitle className="text-xl mb-1">{project.title}</CardTitle>
              {project.short_description && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {project.short_description}
                </p>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Funding Progress */}
          <div className="space-y-2">
            <ProgressBar
              value={project.raised_percent}
              showLabel={true}
            />
            
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">
                {formatCurrency(project.raised_amount)} de {formatCurrency(project.target_amount)}
              </span>
              <span className="font-medium">{formatPercent(project.raised_percent)}</span>
            </div>
          </div>

          {/* Club Contribution Rule */}
          {!project.club_contribution_triggered && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-3 rounded-lg bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20"
            >
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="text-sm font-medium text-primary">Regla de Co-Inversión</span>
              </div>
              <p className="text-xs text-muted-foreground">
                {clubRule}
              </p>
            </motion.div>
          )}

          {/* Club Contribution Triggered */}
          {project.club_contribution_triggered && (
            <div className="p-3 rounded-lg bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-900">
              <div className="flex items-center gap-2 mb-1">
                <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium text-green-700 dark:text-green-300">Club Invierte</span>
              </div>
              <p className="text-xs text-green-600 dark:text-green-400">
                El Club aporta {project.club_contribution_percent}% ({formatCurrency(project.club_contribution_amount || 0)})
              </p>
            </div>
          )}

          {/* Project Stats */}
          <div className="grid grid-cols-3 gap-4 pt-2">
            <div>
              <p className="text-xs text-muted-foreground">Inversores</p>
              <p className="text-lg font-semibold">{project.investor_count}<span className="text-xs text-muted-foreground">/50</span></p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Retorno</p>
              <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                {project.expected_return_percent || 0}%
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Plazo</p>
              <p className="text-lg font-semibold">{project.expected_duration_months || 0}m</p>
            </div>
          </div>

          {/* Deadline */}
          {daysRemaining !== null && daysRemaining > 0 && (
            <div className={`text-xs ${daysRemaining <= 7 ? 'text-red-600 font-medium' : 'text-muted-foreground'}`}>
              {daysRemaining <= 7 ? '⚠️ ' : ''}
              {daysRemaining} {daysRemaining === 1 ? 'día' : 'días'} restantes
            </div>
          )}

          {/* Invest Button */}
          {onInvest && project.status === 'funding' && (
            <Button
              className="w-full"
              size="lg"
              onClick={() => onInvest(project.id)}
              disabled={project.raised_percent >= 100 || project.investor_count >= 50}
            >
              Invertir Ahora
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

function getClubRule(category: string): string {
  const rules = {
    level_1: '>55% recaudado + 3 meses → Club pone 45%',
    level_2: '>65% recaudado + 6 meses → Club pone 35%',
    level_3: '>75% recaudado + 9 meses → Club pone 25%',
  }
  return rules[category as keyof typeof rules] || ''
}
