
import { useEffect, useState } from 'react'
import {
  getHouseholds,
  getConsumption,
  getAnalytics,
} from '../services/api'

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

// Format numeric values safely
function formatNumber(value, decimals = 2) {
  const number = Number(value)

  return Number.isFinite(number)
    ? number.toFixed(decimals)
    : (0).toFixed(decimals)
}

// Format activity names
function formatActivityName(activity) {
  return activity.charAt(0).toUpperCase() + activity.slice(1)
}

function Dashboard() {
  const [household, setHousehold] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isMounted = true

    async function loadDashboard() {
      try {
        setLoading(true)
        setError('')

        // 1. Retrieve registered households
        const householdResponse = await getHouseholds()
        const households = householdResponse.households || []

        if (households.length === 0) {
          if (isMounted) {
            setHousehold(null)
            setAnalytics(null)
            setRecords([])
            setError('No household has been registered yet.')
          }
          return
        }

        // 2. Select the first registered household
        const selectedHousehold = households[0]

        // 3. Retrieve consumption records and analytics together
        const [
          consumptionResponse,
          analyticsResponse,
        ] = await Promise.all([
          getConsumption(selectedHousehold.household_id),
          getAnalytics(selectedHousehold.household_id),
        ])

        // 4. Sort records chronologically
        const sortedRecords = [
          ...(consumptionResponse.records || []),
        ].sort((a, b) =>
          a.record_date.localeCompare(b.record_date)
        )

        if (isMounted) {
          setHousehold(selectedHousehold)
          setAnalytics(analyticsResponse)
          setRecords(sortedRecords)
        }

      } catch (err) {
        if (isMounted) {
          setError(
            err.message || 'Unable to load dashboard data.'
          )
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      isMounted = false
    }
  }, [])

  // Loading state
  if (loading) {
    return (
      <div className="page-content">
        <p className="empty-state">
          Loading dashboard data...
        </p>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="page-content">
        <div className="page-heading">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h1>Water consumption dashboard</h1>
          </div>
        </div>

        <div className="form-alert error-alert">
          {error}
        </div>
      </div>
    )
  }

  // 5. Identify the latest record
  const latestRecord =
    records.length > 0
      ? records[records.length - 1]
      : null

  const summary = analytics?.summary

  const total = Number(latestRecord?.total_liters) || 0

  // 6. Prepare activity-wise consumption
  const activities = latestRecord
    ? [
        {
          name: 'Bathroom',
          amount: Number(latestRecord.bathroom_liters) || 0,
          color: 'bar-blue',
        },
        {
          name: 'Kitchen',
          amount: Number(latestRecord.kitchen_liters) || 0,
          color: 'bar-teal',
        },
        {
          name: 'Laundry',
          amount: Number(latestRecord.laundry_liters) || 0,
          color: 'bar-purple',
        },
        {
          name: 'Gardening',
          amount: Number(latestRecord.gardening_liters) || 0,
          color: 'bar-green',
        },
      ]
    : []

  // 7. Prepare chronological chart data
  const chartData = records.map((record) => ({
    date: record.record_date,
    consumption: Number(record.total_liters) || 0,
    bathroom: Number(record.bathroom_liters) || 0,
    kitchen: Number(record.kitchen_liters) || 0,
    laundry: Number(record.laundry_liters) || 0,
    gardening: Number(record.gardening_liters) || 0,
  }))

  // 8. Prepare dashboard statistics
  const averageConsumption =
    Number(summary?.average_per_record_liters) || 0

  const perPersonConsumption =
    Number(summary?.average_per_person_per_record_liters) || 0

  const totalConsumption =
    Number(summary?.total_consumption_liters) || 0

  const totalRecords =
    Number(summary?.total_records) || 0

  return (
    <div className="page-content">

      {/* Page heading */}
      <div className="page-heading">
        <div>
          <p className="eyebrow">OVERVIEW</p>

          <h1>Water consumption dashboard</h1>

          <p className="page-description">
            Monitor household water usage using recorded consumption data.
          </p>
        </div>

        <span className="sample-badge">
          LIVE DATABASE DATA
        </span>
      </div>

      {/* Statistics */}
      <section className="stats-grid">

        <StatCard
          label="Latest recorded consumption"
          value={latestRecord ? formatNumber(total) : '0'}
          unit="L"
          note={latestRecord?.record_date || 'No records available'}
          icon="💧"
          color="blue"
        />

        <StatCard
          label="Household members"
          value={household?.household_size || 0}
          unit=""
          note={household?.household_name || 'Registered household'}
          icon="👥"
          color="purple"
        />

        <StatCard
          label="Average daily consumption"
          value={formatNumber(averageConsumption)}
          unit="L"
          note="Average across recorded days"
          icon="📊"
          color="teal"
        />

        <StatCard
          label="Total records"
          value={totalRecords}
          unit=""
          note="Recorded household days"
          icon="📅"
          color="green"
        />

      </section>

      {/* Consumption breakdown and insights */}
      <section className="dashboard-grid">

        <article className="panel consumption-panel">

          <div className="panel-heading">
            <div>
              <h2>Latest consumption breakdown</h2>
              <p>Recorded usage by activity</p>
            </div>

            <span className="panel-tag">
              {formatNumber(total)} L total
            </span>
          </div>

          {latestRecord ? (
            <div className="breakdown-list">

              {activities.map((item) => {
                const percentage =
                  total > 0
                    ? (item.amount / total) * 100
                    : 0

                return (
                  <div
                    className="breakdown-item"
                    key={item.name}
                  >
                    <div className="breakdown-info">
                      <span>{item.name}</span>

                      <strong>
                        {formatNumber(item.amount)} L
                      </strong>
                    </div>

                    <div className="progress-track">
                      <div
                        className={`progress-fill ${item.color}`}
                        style={{
                          width: `${percentage}%`,
                        }}
                      />
                    </div>

                    <span className="breakdown-percent">
                      {percentage.toFixed(1)}%
                    </span>
                  </div>
                )
              })}

            </div>
          ) : (
            <div className="empty-state">
              No consumption records have been added yet.
            </div>
          )}

        </article>

        {/* Household insights */}
        <article className="panel insight-panel">

          <div className="panel-heading">
            <div>
              <h2>Household insights</h2>
              <p>Calculated from recorded consumption</p>
            </div>

            <span className="insight-symbol">✦</span>
          </div>

          <div className="insight-number">
            {formatNumber(perPersonConsumption)} L
          </div>

          <p className="insight-description">
            Average water consumption per household member per recorded day.
          </p>

          <div className="insight-divider" />

          <div className="insight-row">
            <span>Total recorded consumption</span>

            <strong>
              {formatNumber(totalConsumption)} L
            </strong>
          </div>

          <div className="insight-row">
            <span>Recorded days</span>

            <strong>{totalRecords}</strong>
          </div>

          <div className="insight-row">
            <span>Highest consuming activity</span>

            <strong className="positive-value">
              {analytics?.highest_consuming_activity
                ? formatActivityName(
                    analytics.highest_consuming_activity
                  )
                : 'N/A'}
            </strong>
          </div>

        </article>

      </section>

      {/* Overall consumption trend */}
      <section className="panel trend-panel">

        <div className="panel-heading">
          <div>
            <h2>Daily water consumption trend</h2>
            <p>Historical household consumption in litres</p>
          </div>

          <span className="panel-tag">
            RECORDED DATA
          </span>
        </div>

        {chartData.length > 0 ? (
          <div className="trend-chart">

            <ResponsiveContainer width="100%" height="100%">

              <LineChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 5,
                  bottom: 5,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e8eff0"
                />

                <XAxis
                  dataKey="date"
                  tick={{
                    fill: '#829399',
                    fontSize: 11,
                  }}
                />

                <YAxis
                  tick={{
                    fill: '#829399',
                    fontSize: 11,
                  }}
                  unit=" L"
                />

                <Tooltip
                  formatter={(value) => [
                    `${formatNumber(value)} L`,
                    'Consumption',
                  ]}
                  labelFormatter={(label) => `Date: ${label}`}
                />

                <Line
                  type="monotone"
                  dataKey="consumption"
                  name="Total consumption"
                  stroke="#159a8a"
                  strokeWidth={3}
                  dot={{
                    r: 5,
                    fill: '#159a8a',
                  }}
                  activeDot={{ r: 7 }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>
        ) : (
          <div className="empty-state">
            No historical consumption data available.
          </div>
        )}

      </section>

      {/* Activity-wise consumption trend */}
      <section className="panel trend-panel activity-trend-panel">

        <div className="panel-heading">
          <div>
            <h2>Activity-wise consumption trend</h2>
            <p>
              Historical water usage across household activities
            </p>
          </div>

          <span className="panel-tag">
            ACTIVITY BREAKDOWN
          </span>
        </div>

        {chartData.length > 0 ? (
          <div className="trend-chart">

            <ResponsiveContainer width="100%" height="100%">

              <LineChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 5,
                  bottom: 5,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e8eff0"
                />

                <XAxis
                  dataKey="date"
                  tick={{
                    fill: '#829399',
                    fontSize: 11,
                  }}
                />

                <YAxis
                  tick={{
                    fill: '#829399',
                    fontSize: 11,
                  }}
                  unit=" L"
                />

                <Tooltip
                  formatter={(value, name) => [
                    `${formatNumber(value)} L`,
                    name,
                  ]}
                  labelFormatter={(label) => `Date: ${label}`}
                />

                <Line
                  type="monotone"
                  dataKey="bathroom"
                  name="Bathroom"
                  stroke="#5499d5"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="kitchen"
                  name="Kitchen"
                  stroke="#27a89a"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="laundry"
                  name="Laundry"
                  stroke="#9981d4"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="gardening"
                  name="Gardening"
                  stroke="#76b77a"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>
        ) : (
          <div className="empty-state">
            No activity-wise historical data available.
          </div>
        )}

      </section>

      {/* Dashboard disclaimer */}
      <div className="dashboard-note">
        Dashboard figures are retrieved from the Flask API and SQLite database.
        Predictions and optimized allocations are displayed separately in their
        respective modules.
      </div>

    </div>
  )
}


// Reusable statistics card
function StatCard({
  label,
  value,
  unit,
  note,
  icon,
  color,
}) {
  return (
    <article className="stat-card">

      <div className="stat-card-top">
        <span className="stat-label">
          {label}
        </span>

        <span className={`stat-icon ${color}`}>
          {icon}
        </span>
      </div>

      <div className="stat-value">
        {value}
        <span>{unit}</span>
      </div>

      <p className="stat-note">
        {note}
      </p>

    </article>
  )
}

export default Dashboard
