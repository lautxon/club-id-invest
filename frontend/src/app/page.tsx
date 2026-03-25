/**
 * Home Page
 * Landing page for Club ID Invest
 */

'use client'

import { Button, Card, CardContent } from '@/components/ui'
import { ProjectCard } from '@/components/ProjectCard'
import { useAuth } from '@/lib/auth-store'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'

export default function HomePage() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  const features = [
    {
      title: 'Co-Inversión Automática',
      description: 'El Club complementa tu inversión automáticamente cuando alcanzás los objetivos',
      icon: '🤝',
    },
    {
      title: '3 Niveles de Inversor',
      description: 'Cebollitas, 1ra Div y Senior. Cada nivel tiene beneficios únicos',
      icon: '📊',
    },
    {
      title: 'Fideicomisos Seguros',
      description: 'Inversiones respaldadas legalmente con contratos digitales',
      icon: '🔒',
    },
  ]

  const sampleProjects = [
    {
      id: 1,
      title: 'Residencial Norte',
      short_description: 'Desarrollo residencial en zona norte',
      category: 'level_1' as const,
      target_amount: 100000,
      minimum_investment: 100,
      raised_amount: 55000,
      raised_percent: 55,
      investor_count: 28,
      club_contribution_percent: 0,
      club_contribution_amount: 0,
      club_contribution_triggered: false,
      status: 'funding' as const,
      expected_return_percent: 12,
      expected_duration_months: 18,
    },
    {
      id: 2,
      title: 'Oficinas Centro',
      short_description: 'Torre de oficinas en microcentro',
      category: 'level_2' as const,
      target_amount: 500000,
      minimum_investment: 5000,
      raised_amount: 325000,
      raised_percent: 65,
      investor_count: 42,
      club_contribution_percent: 0,
      club_contribution_amount: 0,
      club_contribution_triggered: false,
      status: 'funding' as const,
      expected_return_percent: 15,
      expected_duration_months: 24,
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-3xl mx-auto"
        >
          <h1 className="text-5xl md:text-6xl font-bold tracking-tighter mb-6">
            Invertí en Proyectos Inmobiliarios con el Club
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Plataforma de inversión colectiva a través de fideicomisos. 
            El Club complementa tu inversión automáticamente.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" onClick={() => router.push('/register')}>
              Empezar Ahora
            </Button>
            <Button size="lg" variant="outline" onClick={() => router.push('/login')}>
              Iniciar Sesión
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16 max-w-7xl">
        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Investment Tiers */}
      <section className="container mx-auto px-4 py-16 max-w-7xl">
        <h2 className="text-3xl font-bold text-center mb-12">Niveles de Inversor</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <TierCard
            name="Cebollitas"
            requirement=">55% recaudado + 3 meses"
            clubContribution="45%"
            minInvestment="$100"
            color="from-green-500/10 to-green-500/5"
            border="border-green-200"
          />
          <TierCard
            name="1ra Div"
            requirement=">65% recaudado + 6 meses"
            clubContribution="35%"
            minInvestment="$5,000"
            color="from-blue-500/10 to-blue-500/5"
            border="border-blue-200"
          />
          <TierCard
            name="Senior"
            requirement=">75% recaudado + 9 meses"
            clubContribution="25%"
            minInvestment="$25,000"
            color="from-purple-500/10 to-purple-500/5"
            border="border-purple-200"
          />
        </div>
      </section>

      {/* Sample Projects */}
      <section className="container mx-auto px-4 py-16 max-w-7xl">
        <h2 className="text-3xl font-bold mb-8">Proyectos Destacados</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {sampleProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 max-w-7xl">
        <Card className="bg-primary text-primary-foreground">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">¿Listo para empezar?</h2>
            <p className="text-lg opacity-90 mb-8 max-w-2xl mx-auto">
              Unite al Club y empezá a invertir en proyectos inmobiliarios con co-inversión automática
            </p>
            <Button size="lg" variant="secondary" onClick={() => router.push('/register')}>
              Crear Cuenta Gratis
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="text-center text-sm text-muted-foreground">
          <p>© 2026 Club ID Invest. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  )
}

interface TierCardProps {
  name: string
  requirement: string
  clubContribution: string
  minInvestment: string
  color: string
  border: string
}

function TierCard({ name, requirement, clubContribution, minInvestment, color, border }: TierCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card className={`bg-gradient-to-br ${color} ${border} border-2`}>
        <CardContent className="p-6 text-center">
          <h3 className="text-2xl font-bold mb-4">{name}</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Requisitos</p>
              <p className="font-medium">{requirement}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Aporte del Club</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">{clubContribution}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Inversión Mínima</p>
              <p className="font-medium">{minInvestment}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
