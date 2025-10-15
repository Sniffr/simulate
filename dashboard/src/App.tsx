import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { TrendingUp, TrendingDown, Trophy, Target, BarChart3, Activity, Percent } from 'lucide-react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL

interface SimulationData {
  home_team: string
  away_team: string
  final_score: Record<string, number>
  bet_slip_won: boolean
  bet_results: Array<{
    market: string
    outcome: string
    won: boolean
    stake: number | null
    odds: number | null
    payout: number | null
    profit: number | null
    explanation: string
  }>
  total_stake: number | null
  total_payout: number | null
  total_profit: number | null
  simulation_metadata: {
    rtp: number
    volatility: string
    seed: number
    total_events: number
    number_of_bets: number
  }
}

function App() {
  const [rtp, setRtp] = useState<number>(0.96)
  const [loading, setLoading] = useState(false)
  const [simulations, setSimulations] = useState<SimulationData[]>([])
  const [stats, setStats] = useState({
    totalBets: 0,
    wonBets: 0,
    lostBets: 0,
    totalStaked: 0,
    totalPayout: 0,
    actualRtp: 0
  })

  useEffect(() => {
    fetchRtp()
  }, [])

  useEffect(() => {
    calculateStats()
  }, [simulations])

  const fetchRtp = async () => {
    try {
      const response = await fetch(`${API_URL}/api/rtp`)
      const data = await response.json()
      setRtp(data.rtp)
    } catch (error) {
      console.error('Error fetching RTP:', error)
    }
  }

  const updateRtp = async (newRtp: number) => {
    try {
      await fetch(`${API_URL}/api/rtp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rtp: newRtp })
      })
      setRtp(newRtp)
    } catch (error) {
      console.error('Error updating RTP:', error)
    }
  }

  const runSimulation = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          home_team: "Manchester United",
          away_team: "Arsenal",
          score_probabilities: [
            { home_score: 0, away_score: 0, probability: 0.10 },
            { home_score: 1, away_score: 0, probability: 0.25 },
            { home_score: 2, away_score: 0, probability: 0.15 },
            { home_score: 2, away_score: 1, probability: 0.15 },
            { home_score: 1, away_score: 1, probability: 0.10 },
            { home_score: 3, away_score: 1, probability: 0.05 },
            { home_score: 0, away_score: 1, probability: 0.08 },
            { home_score: 1, away_score: 2, probability: 0.07 },
            { home_score: 3, away_score: 2, probability: 0.05 }
          ],
          bet_slip: [
            { market: "1X2", outcome: "1", stake: 100, odds: 2.1 },
            { market: "over_under", outcome: "over_2.5", stake: 50, odds: 1.9 }
          ],
          volatility: "medium"
        })
      })
      const data = await response.json()
      setSimulations(prev => [data, ...prev].slice(0, 20))
    } catch (error) {
      console.error('Error running simulation:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateStats = () => {
    let totalBets = 0
    let wonBets = 0
    let lostBets = 0
    let totalStaked = 0
    let totalPayout = 0

    simulations.forEach(sim => {
      sim.bet_results.forEach(bet => {
        if (bet.stake !== null) {
          totalBets++
          totalStaked += bet.stake
          if (bet.won) {
            wonBets++
            totalPayout += bet.payout || 0
          } else {
            lostBets++
          }
        }
      })
    })

    const actualRtp = totalStaked > 0 ? (totalPayout / totalStaked) : 0

    setStats({
      totalBets,
      wonBets,
      lostBets,
      totalStaked,
      totalPayout,
      actualRtp
    })
  }

  const rtpDifference = stats.actualRtp - rtp
  const rtpColor = Math.abs(rtpDifference) < 0.05 ? 'text-green-600' : 'text-yellow-600'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <div className="bg-black bg-opacity-40 backdrop-blur-sm border-b border-white border-opacity-10">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white flex items-center gap-3">
                <Trophy className="text-yellow-400" size={40} />
                Football Betting Simulator
              </h1>
              <p className="text-blue-200 mt-2">Real-time RTP tracking and betting analytics</p>
            </div>
            <Button 
              onClick={runSimulation} 
              disabled={loading}
              size="lg"
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold shadow-lg"
            >
              {loading ? 'Simulating...' : '⚽ Run New Simulation'}
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Configured RTP */}
          <Card className="bg-gradient-to-br from-blue-500 to-blue-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Target size={24} />
                Configured RTP
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold">{(rtp * 100).toFixed(1)}%</div>
              <div className="mt-4 flex gap-2">
                <Button 
                  size="sm" 
                  variant="secondary"
                  onClick={() => updateRtp(0.96)}
                  className="flex-1"
                >
                  96%
                </Button>
                <Button 
                  size="sm" 
                  variant="secondary"
                  onClick={() => updateRtp(0.92)}
                  className="flex-1"
                >
                  92%
                </Button>
                <Button 
                  size="sm" 
                  variant="secondary"
                  onClick={() => updateRtp(0.88)}
                  className="flex-1"
                >
                  88%
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Actual RTP */}
          <Card className="bg-gradient-to-br from-purple-500 to-purple-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Percent size={24} />
                Actual RTP
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold">{(stats.actualRtp * 100).toFixed(1)}%</div>
              <div className={`mt-2 flex items-center gap-2 ${rtpColor}`}>
                {rtpDifference >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                <span className="font-semibold">
                  {rtpDifference >= 0 ? '+' : ''}{(rtpDifference * 100).toFixed(1)}% vs target
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Total Bets */}
          <Card className="bg-gradient-to-br from-green-500 to-green-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Activity size={24} />
                Total Bets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold">{stats.totalBets}</div>
              <div className="mt-2 flex gap-3">
                <div className="flex items-center gap-1">
                  <Badge variant="secondary" className="bg-green-900">
                    ✓ {stats.wonBets}
                  </Badge>
                </div>
                <div className="flex items-center gap-1">
                  <Badge variant="secondary" className="bg-red-900">
                    ✗ {stats.lostBets}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Profit/Loss */}
          <Card className={`bg-gradient-to-br ${stats.totalPayout - stats.totalStaked >= 0 ? 'from-emerald-500 to-emerald-700' : 'from-red-500 to-red-700'} border-none text-white`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <BarChart3 size={24} />
                House Profit
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold">
                ${(stats.totalStaked - stats.totalPayout).toFixed(2)}
              </div>
              <div className="mt-2 text-sm opacity-90">
                Staked: ${stats.totalStaked.toFixed(2)} | Paid: ${stats.totalPayout.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Simulations */}
        <Card className="bg-white bg-opacity-10 backdrop-blur-md border-white border-opacity-20">
          <CardHeader>
            <CardTitle className="text-white text-2xl">Recent Simulations</CardTitle>
            <CardDescription className="text-blue-200">
              Latest {simulations.length} match simulations with betting outcomes
            </CardDescription>
          </CardHeader>
          <CardContent>
            {simulations.length === 0 ? (
              <div className="text-center py-12 text-white opacity-60">
                <Trophy size={64} className="mx-auto mb-4 opacity-30" />
                <p className="text-xl">No simulations yet</p>
                <p className="text-sm mt-2">Click "Run New Simulation" to get started</p>
              </div>
            ) : (
              <div className="space-y-4">
                {simulations.map((sim, idx) => (
                  <div 
                    key={idx}
                    className="bg-white bg-opacity-5 rounded-lg p-6 border border-white border-opacity-10 hover:bg-opacity-10 transition-all"
                  >
                    {/* Match Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <div className="text-2xl font-bold text-white">
                          {sim.home_team} vs {sim.away_team}
                        </div>
                        <Badge variant="secondary" className="text-lg">
                          {sim.final_score[sim.home_team]} - {sim.final_score[sim.away_team]}
                        </Badge>
                      </div>
                      <Badge 
                        className={`text-lg px-4 py-1 ${sim.bet_slip_won ? 'bg-green-600' : 'bg-red-600'}`}
                      >
                        {sim.bet_slip_won ? '✓ Slip Won' : '✗ Slip Lost'}
                      </Badge>
                    </div>

                    <Separator className="my-4 bg-white opacity-10" />

                    {/* Bet Results */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {sim.bet_results.map((bet, betIdx) => (
                        <div 
                          key={betIdx}
                          className={`p-4 rounded-lg border-2 ${bet.won ? 'border-green-500 bg-green-500 bg-opacity-10' : 'border-red-500 bg-red-500 bg-opacity-10'}`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-white">{bet.market}</span>
                            <Badge variant={bet.won ? "default" : "destructive"} className="font-bold">
                              {bet.outcome}
                            </Badge>
                          </div>
                          {bet.stake !== null && (
                            <div className="text-sm space-y-1 text-blue-100">
                              <div>Stake: ${bet.stake.toFixed(2)} @ {bet.odds}x</div>
                              {bet.won && <div className="font-bold text-green-300">Payout: ${bet.payout?.toFixed(2)} (+${bet.profit?.toFixed(2)})</div>}
                              {!bet.won && <div className="font-bold text-red-300">Lost ${bet.stake.toFixed(2)}</div>}
                            </div>
                          )}
                          {bet.stake === null && (
                            <div className="text-sm text-blue-100">
                              {bet.won ? '✓ Prediction correct' : '✗ Prediction incorrect'}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Totals */}
                    {sim.total_stake !== null && (
                      <div className="bg-black bg-opacity-30 rounded-lg p-4 flex justify-between items-center">
                        <div className="text-white">
                          <div className="text-sm opacity-75">Total Stake</div>
                          <div className="text-2xl font-bold">${sim.total_stake.toFixed(2)}</div>
                        </div>
                        <div className="text-white">
                          <div className="text-sm opacity-75">Total Payout</div>
                          <div className="text-2xl font-bold">${sim.total_payout?.toFixed(2)}</div>
                        </div>
                        <div className={`${sim.total_profit && sim.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          <div className="text-sm opacity-75">Profit/Loss</div>
                          <div className="text-2xl font-bold">
                            {sim.total_profit && sim.total_profit >= 0 ? '+' : ''}${sim.total_profit?.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="mt-4 flex gap-4 text-sm text-blue-200">
                      <span>Seed: {sim.simulation_metadata.seed}</span>
                      <span>•</span>
                      <span>Events: {sim.simulation_metadata.total_events}</span>
                      <span>•</span>
                      <span>Volatility: {sim.simulation_metadata.volatility}</span>
                      <span>•</span>
                      <span>RTP: {(sim.simulation_metadata.rtp * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
