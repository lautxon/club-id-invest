/**
 * AlertSystem Component
 * Displays investment alerts with severity-based styling
 */

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, Alert, Badge, Button } from './ui'
import { dashboardAPI, type InvestmentAlert as InvestmentAlertType } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { getSeverityColor } from '@/lib/utils'

interface AlertItem {
  investment_id: number
  project_title: string
  alert_type: 'funding_deadline' | 'payment_pending' | 'return_expected'
  message: string
  days_remaining?: number
  severity: 'info' | 'warning' | 'critical'
}

interface AlertSystemProps {
  userId?: number
  limit?: number
  showDismiss?: boolean
}

export function AlertSystem({ userId, limit = 10, showDismiss = true }: AlertSystemProps) {
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<number>>(new Set())

  const { data: alertsData, isLoading, refetch } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const response = await dashboardAPI.getAlerts()
      return response.data as AlertItem[]
    },
    refetchInterval: 60000, // Refresh every minute
  })

  const alerts = alertsData?.filter(alert => !dismissedAlerts.has(alert.investment_id)) || []

  const handleDismiss = (alertId: number) => {
    setDismissedAlerts(prev => new Set(prev).add(alertId))
  }

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'funding_deadline':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'payment_pending':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'return_expected':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-secondary rounded w-1/4"></div>
            <div className="h-4 bg-secondary rounded w-3/4"></div>
            <div className="h-4 bg-secondary rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (alerts.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center py-4">
            <svg className="w-12 h-12 mx-auto text-muted-foreground/50 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-muted-foreground">Sin alertas pendientes</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-lg">Alertas</h3>
            <Badge variant="destructive" className="animate-pulse">
              {alerts.length}
            </Badge>
          </div>
        </div>

        <AnimatePresence>
          <div className="divide-y max-h-[400px] overflow-y-auto">
            {alerts.slice(0, limit).map((alert, index) => (
              <motion.div
                key={alert.investment_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                className="p-4 hover:bg-secondary/50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className={getSeverityColor(alert.severity).split(' ')[0] + ' p-2 rounded-full'}>
                    {getAlertIcon(alert.alert_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={getSeverityColor(alert.severity)}>
                        <AlertTitle severity={alert.severity} />
                      </span>
                      {alert.days_remaining !== undefined && (
                        <Badge variant={alert.days_remaining <= 7 ? 'error' : 'warning'}>
                          {alert.days_remaining} {alert.days_remaining === 1 ? 'día' : 'días'}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-foreground mb-1">{alert.message}</p>
                    <p className="text-xs text-muted-foreground truncate">{alert.project_title}</p>
                  </div>

                  {showDismiss && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDismiss(alert.investment_id)}
                      className="flex-shrink-0 -mr-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </Button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </AnimatePresence>

        {alerts.length > limit && (
          <div className="p-4 border-t text-center">
            <Button variant="ghost" size="sm">
              Ver {alerts.length - limit} alertas más
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function AlertTitle({ severity }: { severity: 'info' | 'warning' | 'critical' }) {
  const titles = {
    info: 'Información',
    warning: 'Advertencia',
    critical: 'Crítico',
  }
  return titles[severity]
}

// Alert display component for inline usage
export function AlertDisplay({ alert }: { alert: AlertItem }) {
  return (
    <Alert variant={alert.severity === 'critical' ? 'error' : alert.severity === 'warning' ? 'warning' : 'info'}>
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <p className="font-medium">{alert.message}</p>
          <p className="text-sm opacity-80 mt-1">{alert.project_title}</p>
        </div>
        {alert.days_remaining !== undefined && (
          <Badge variant={alert.days_remaining <= 7 ? 'error' : 'warning'}>
            {alert.days_remaining}d
          </Badge>
        )}
      </div>
    </Alert>
  )
}
