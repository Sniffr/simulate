import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Trophy, Target, BarChart3, Activity, Percent, Search, RefreshCw, Database, Play, Pause } from 'lucide-react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL

interface HistoricalSimulation {
  id: number
  home_team: string
  away_team: string
  home_score: number
  away_score: number
  bet_slip_won: boolean
  total_stake: number | null
  total_payout: number | null
  total_profit: number | null
  configured_rtp: number
  created_at: string
  number_of_bets: number
}

interface Stats {
  total_simulations: number
  won_slips: number
  lost_slips: number
  total_bets: number
  total_staked: number
  total_paid_out: number
  house_profit: number
  actual_rtp: number
  avg_configured_rtp: number
  rtp_difference: number
}

interface RTPTrend {
  simulation_number: number
  created_at: string
  configured_rtp: number
  cumulative_actual_rtp: number
  rolling_window_rtp: number
}

function App() {
  const [rtp, setRtp] = useState<number>(0.96)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<Stats | null>(null)
  const [history, setHistory] = useState<HistoricalSimulation[]>([])
  const [rtpTrends, setRtpTrends] = useState<RTPTrend[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterWon, setFilterWon] = useState<boolean | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState<number>(5)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    fetchAll()
  }, [])

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => {
        fetchAll()
      }, refreshInterval * 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [autoRefresh, refreshInterval])

  const fetchAll = async () => {
    await Promise.all([
      fetchRtp(),
      fetchStats(),
      fetchHistory(),
      fetchRTPTrends()
    ])
  }

  const fetchRtp = async () => {
    try {
      const response = await fetch(`${API_URL}/api/rtp`)
      const data = await response.json()
      setRtp(data.rtp)
    } catch (error) {
      console.error('Error fetching RTP:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stats`)
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchHistory = async () => {
    try {
      let url = `${API_URL}/api/history?limit=50`
      if (searchTerm) url += `&team=${encodeURIComponent(searchTerm)}`
      if (filterWon !== null) url += `&won=${filterWon}`
      
      const response = await fetch(url)
      const data = await response.json()
      setHistory(data.simulations)
    } catch (error) {
      console.error('Error fetching history:', error)
    }
  }

  const fetchRTPTrends = async () => {
    try {
      const response = await fetch(`${API_URL}/api/rtp-trends?limit=100`)
      const data = await response.json()
      setRtpTrends(data.trends)
    } catch (error) {
      console.error('Error fetching RTP trends:', error)
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
      await fetch(`${API_URL}/api/simulate`, {
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
      
      await fetchAll()
    } catch (error) {
      console.error('Error running simulation:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchHistory()
  }

  const rtpDifference = stats ? stats.rtp_difference : 0
  const rtpColor = Math.abs(rtpDifference) < 0.05 ? 'text-green-400' : 'text-yellow-400'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="bg-black bg-opacity-40 backdrop-blur-sm border-b border-white border-opacity-10">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white flex items-center gap-3">
                <Trophy className="text-yellow-400" size={40} />
                Football Betting Simulator
              </h1>
              <p className="text-blue-200 mt-2">Historical RTP tracking and betting analytics</p>
            </div>
            <div className="flex gap-3 items-center">
              <div className="flex gap-2 items-center bg-black bg-opacity-30 px-4 py-2 rounded-lg border border-white border-opacity-10">
                <Button 
                  onClick={() => setAutoRefresh(!autoRefresh)} 
                  variant="outline"
                  size="sm"
                  className={`${autoRefresh ? 'border-green-400 text-green-400' : 'border-gray-400 text-gray-400'}`}
                >
                  {autoRefresh ? <Pause size={16} className="mr-1" /> : <Play size={16} className="mr-1" />}
                  {autoRefresh ? 'Stop' : 'Auto'}
                </Button>
                <Select value={refreshInterval.toString()} onValueChange={(val) => setRefreshInterval(Number(val))}>
                  <SelectTrigger className="w-24 bg-white bg-opacity-10 border-white border-opacity-20 text-white text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="3">3s</SelectItem>
                    <SelectItem value="5">5s</SelectItem>
                    <SelectItem value="10">10s</SelectItem>
                    <SelectItem value="30">30s</SelectItem>
                    <SelectItem value="60">60s</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button 
                onClick={fetchAll} 
                variant="outline"
                size="lg"
                className="border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white"
              >
                <RefreshCw size={20} className="mr-2" />
                Refresh
              </Button>
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
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white text-sm">
                <Target size={20} />
                Configured RTP
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{(rtp * 100).toFixed(1)}%</div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="secondary" onClick={() => updateRtp(0.96)} className="flex-1 text-xs">96%</Button>
                <Button size="sm" variant="secondary" onClick={() => updateRtp(0.92)} className="flex-1 text-xs">92%</Button>
                <Button size="sm" variant="secondary" onClick={() => updateRtp(0.88)} className="flex-1 text-xs">88%</Button>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white text-sm">
                <Percent size={20} />
                Actual RTP
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{((stats?.actual_rtp || 0) * 100).toFixed(1)}%</div>
              <div className={`mt-2 flex items-center gap-2 ${rtpColor}`}>
                {rtpDifference >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                <span className="font-semibold text-xs">
                  {rtpDifference >= 0 ? '+' : ''}{(rtpDifference * 100).toFixed(1)}% vs target
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-green-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white text-sm">
                <Database size={20} />
                Total Simulations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats?.total_simulations || 0}</div>
              <div className="mt-2 flex gap-2 text-xs">
                <Badge variant="secondary" className="bg-green-900">✓ {stats?.won_slips || 0}</Badge>
                <Badge variant="secondary" className="bg-red-900">✗ {stats?.lost_slips || 0}</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500 to-orange-700 border-none text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white text-sm">
                <Activity size={20} />
                Total Bets
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{stats?.total_bets || 0}</div>
              <div className="mt-2 text-xs opacity-90">
                Staked: ${(stats?.total_staked || 0).toFixed(0)}
              </div>
            </CardContent>
          </Card>

          <Card className={`bg-gradient-to-br ${(stats?.house_profit || 0) >= 0 ? 'from-emerald-500 to-emerald-700' : 'from-red-500 to-red-700'} border-none text-white`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white text-sm">
                <BarChart3 size={20} />
                House Profit
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">
                ${(stats?.house_profit || 0).toFixed(0)}
              </div>
              <div className="mt-2 text-xs opacity-90">
                Paid: ${(stats?.total_paid_out || 0).toFixed(0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {rtpTrends.length > 0 && (
          <Card className="bg-white bg-opacity-10 backdrop-blur-md border-white border-opacity-20 mb-8">
            <CardHeader>
              <CardTitle className="text-white text-2xl">RTP Trends Over Time</CardTitle>
              <CardDescription className="text-blue-200">
                Configured vs Actual RTP across {rtpTrends.length} simulations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={rtpTrends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="simulation_number" 
                    stroke="rgba(255,255,255,0.7)"
                    label={{ value: 'Simulation Number', position: 'insideBottom', offset: -5, fill: 'rgba(255,255,255,0.7)' }}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.7)"
                    label={{ value: 'RTP', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.7)' }}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="configured_rtp" stroke="#3b82f6" name="Configured RTP" strokeWidth={2} />
                  <Line type="monotone" dataKey="cumulative_actual_rtp" stroke="#a855f7" name="Cumulative Actual RTP" strokeWidth={2} />
                  <Line type="monotone" dataKey="rolling_window_rtp" stroke="#10b981" name="Rolling Window RTP (10)" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        <Card className="bg-white bg-opacity-10 backdrop-blur-md border-white border-opacity-20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white text-2xl">Simulation History</CardTitle>
                <CardDescription className="text-blue-200">
                  All simulations from the database
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Input
                  type="text"
                  placeholder="Search by team..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64 bg-white bg-opacity-10 border-white border-opacity-20 text-white placeholder:text-gray-400"
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch} size="sm" variant="outline" className="border-blue-400 text-blue-400">
                  <Search size={16} />
                </Button>
                <Button 
                  onClick={() => { setFilterWon(null); setSearchTerm(''); fetchHistory(); }} 
                  size="sm" 
                  variant="outline"
                  className="border-gray-400 text-gray-400"
                >
                  Clear
                </Button>
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              <Badge 
                className={`cursor-pointer ${filterWon === true ? 'bg-green-600' : 'bg-gray-600'}`}
                onClick={() => { setFilterWon(true); setTimeout(fetchHistory, 0); }}
              >
                Won Slips
              </Badge>
              <Badge 
                className={`cursor-pointer ${filterWon === false ? 'bg-red-600' : 'bg-gray-600'}`}
                onClick={() => { setFilterWon(false); setTimeout(fetchHistory, 0); }}
              >
                Lost Slips
              </Badge>
              <Badge 
                className={`cursor-pointer ${filterWon === null ? 'bg-blue-600' : 'bg-gray-600'}`}
                onClick={() => { setFilterWon(null); setTimeout(fetchHistory, 0); }}
              >
                All
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="text-center py-12 text-white opacity-60">
                <Database size={64} className="mx-auto mb-4 opacity-30" />
                <p className="text-xl">No simulations found</p>
                <p className="text-sm mt-2">Run a simulation to see data here</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-white border-opacity-10 hover:bg-transparent">
                      <TableHead className="text-blue-200">ID</TableHead>
                      <TableHead className="text-blue-200">Match</TableHead>
                      <TableHead className="text-blue-200">Score</TableHead>
                      <TableHead className="text-blue-200">Result</TableHead>
                      <TableHead className="text-blue-200">Stake</TableHead>
                      <TableHead className="text-blue-200">Payout</TableHead>
                      <TableHead className="text-blue-200">Profit</TableHead>
                      <TableHead className="text-blue-200">RTP</TableHead>
                      <TableHead className="text-blue-200">Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {history.map((sim) => (
                      <TableRow 
                        key={sim.id} 
                        className="border-white border-opacity-10 hover:bg-white hover:bg-opacity-5"
                      >
                        <TableCell className="text-white font-mono text-xs">#{sim.id}</TableCell>
                        <TableCell className="text-white">
                          <div className="text-sm font-semibold">{sim.home_team} vs {sim.away_team}</div>
                          <div className="text-xs text-gray-400">{sim.number_of_bets} bets</div>
                        </TableCell>
                        <TableCell className="text-white">
                          <Badge variant="secondary">{sim.home_score} - {sim.away_score}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={sim.bet_slip_won ? 'bg-green-600' : 'bg-red-600'}>
                            {sim.bet_slip_won ? '✓ Won' : '✗ Lost'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-white text-right">
                          {sim.total_stake !== null ? `$${sim.total_stake.toFixed(2)}` : '-'}
                        </TableCell>
                        <TableCell className="text-white text-right">
                          {sim.total_payout !== null ? `$${sim.total_payout.toFixed(2)}` : '-'}
                        </TableCell>
                        <TableCell className={`text-right font-semibold ${(sim.total_profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {sim.total_profit !== null ? `${(sim.total_profit >= 0 ? '+' : '')}$${sim.total_profit.toFixed(2)}` : '-'}
                        </TableCell>
                        <TableCell className="text-white text-right">
                          {(sim.configured_rtp * 100).toFixed(0)}%
                        </TableCell>
                        <TableCell className="text-gray-400 text-xs">
                          {new Date(sim.created_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
