
import { useCallback, useEffect, useState } from 'react'
import { addConsumption, getConsumption } from '../services/api'
import { useHousehold } from '../context/HouseholdContext'

// Get the current date in local timezone (YYYY-MM-DD)
function getLocalDate() {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60000

  return new Date(now.getTime() - offset)
    .toISOString()
    .slice(0, 10)
}

// Initial form values
function createInitialForm() {
  return {
    record_date: getLocalDate(),
    bathroom_liters: '',
    kitchen_liters: '',
    laundry_liters: '',
    gardening_liters: '',
  }
}

const activities = [
  { name: 'bathroom_liters', label: 'Bathroom', icon: '🚿' },
  { name: 'kitchen_liters', label: 'Kitchen', icon: '🍽️' },
  { name: 'laundry_liters', label: 'Laundry', icon: '🧺' },
  { name: 'gardening_liters', label: 'Gardening', icon: '🌱' },
]

function Consumption() {
  const [form, setForm] = useState(createInitialForm)
  const [records, setRecords] = useState([])

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const {
    householdId,
    loadingHousehold,
    householdError,
  } = useHousehold()

  // Calculate total consumption dynamically
  const total = activities.reduce(
    (sum, activity) =>
      sum + (Number(form[activity.name]) || 0),
    0
  )

  // Fetch consumption records from Flask backend
  const loadRecords = useCallback(async () => {
    if (!householdId) return

    setLoading(true)
    setError('')

    try {
      const result = await getConsumption(householdId)
      setRecords(result.records || [])
    } catch (err) {
      setError(err.message || 'Unable to load consumption records.')
    } finally {
      setLoading(false)
    }
  }, [householdId])

  // Load records when household information is available
  useEffect(() => {
    if (loadingHousehold) return

    if (householdError) {
      setError(householdError)
      setLoading(false)
      return
    }

    if (!householdId) {
      setRecords([])
      setLoading(false)
      return
    }

    loadRecords()
  }, [
    loadingHousehold,
    householdError,
    householdId,
    loadRecords,
  ])

  // Handle input changes
  function handleChange(event) {
    const { name, value } = event.target

    setForm(previous => ({
      ...previous,
      [name]: value,
    }))

    setError('')
    setMessage('')
  }

  // Submit consumption data
  async function handleSubmit(event) {
    event.preventDefault()

    if (!householdId) {
      setError('Please register a household first.')
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const payload = {
        household_id: householdId,
        record_date: form.record_date,
        bathroom_liters: Number(form.bathroom_liters),
        kitchen_liters: Number(form.kitchen_liters),
        laundry_liters: Number(form.laundry_liters),
        gardening_liters: Number(form.gardening_liters),
      }

      // Send data to Flask backend
      const result = await addConsumption(payload)

      // Display success message
      setMessage(
        `Consumption recorded successfully! Total: ${result.total_liters.toFixed(2)} L`
      )

      // Reset form only after successful submission
      setForm(createInitialForm())

      // Refresh consumption history
      await loadRecords()

    } catch (err) {
      setError(err.message || 'Unable to save consumption record.')
    } finally {
      setSaving(false)
    }
  }

  // Wait until household information is loaded
  if (loadingHousehold) {
    return (
      <div className="page-content">
        <p className="empty-state">
          Loading household information...
        </p>
      </div>
    )
  }

  // Handle missing household
  if (!householdId) {
    return (
      <div className="page-content">
        <div className="form-alert error-alert">
          {householdError ||
            'Please register a household from the Dashboard first.'}
        </div>
      </div>
    )
  }

  return (
    <div className="page-content">

      {/* Page heading */}
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE / CONSUMPTION</p>

          <h1>Consumption tracker</h1>

          <p className="page-description">
            Record and monitor your household's daily water usage.
          </p>
        </div>

        <span className="sample-badge">
          HOUSEHOLD #{householdId}
        </span>
      </div>

      {/* Consumption entry form */}
      <section className="panel tracker-panel">

        <div className="panel-heading">
          <div>
            <h2>Add daily consumption</h2>
            <p>
              Enter the amount of water used for each activity in litres.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>

          {/* Date input */}
          <div className="form-field date-field">
            <label htmlFor="record_date">
              Record date
            </label>

            <input
              id="record_date"
              type="date"
              name="record_date"
              value={form.record_date}
              onChange={handleChange}
              max={getLocalDate()}
              required
            />
          </div>

          {/* Activity-wise consumption inputs */}
          <div className="consumption-form-grid">

            {activities.map(activity => (
              <div className="form-field" key={activity.name}>

                <label htmlFor={activity.name}>
                  <span>{activity.icon}</span>
                  {' '}
                  {activity.label} (Litres)
                </label>

                <input
                  id={activity.name}
                  type="number"
                  name={activity.name}
                  min="0"
                  step="0.01"
                  placeholder="Enter litres"
                  value={form[activity.name]}
                  onChange={handleChange}
                  required
                />

              </div>
            ))}

          </div>

          {/* Automatically calculated total */}
          <div className="total-preview">

            <div>
              <span>Calculated daily consumption</span>

              <small>
                Automatically calculated from the four activities
              </small>
            </div>

            <strong>{total.toFixed(2)} L</strong>

          </div>

          {/* Feedback messages */}
          {error && (
            <div className="form-alert error-alert">
              {error}
            </div>
          )}

          {message && (
            <div className="form-alert success-alert">
              {message}
            </div>
          )}

          {/* Submit button */}
          <button
            className="submit-button"
            type="submit"
            disabled={saving || loading}
          >
            {saving
              ? 'Saving record...'
              : 'Save consumption record'}
          </button>

        </form>

      </section>

      {/* Consumption history */}
      <section className="panel records-panel">

        <div className="panel-heading">

          <div>
            <h2>Consumption history</h2>

            <p>
              Records retrieved from your Flask backend.
            </p>
          </div>

          <span className="panel-tag">
            {records.length} records
          </span>

        </div>

        {loading ? (

          <p className="empty-state">
            Loading consumption records...
          </p>

        ) : records.length === 0 ? (

          <p className="empty-state">
            No consumption records found.
          </p>

        ) : (

          <div className="table-wrapper">

            <table className="records-table">

              <thead>
                <tr>
                  <th>Date</th>
                  <th>Bathroom</th>
                  <th>Kitchen</th>
                  <th>Laundry</th>
                  <th>Gardening</th>
                  <th>Total</th>
                </tr>
              </thead>

              <tbody>

                {records.map(record => (
                  <tr key={record.record_id}>

                    <td>{record.record_date}</td>

                    <td>
                      {Number(record.bathroom_liters).toFixed(2)} L
                    </td>

                    <td>
                      {Number(record.kitchen_liters).toFixed(2)} L
                    </td>

                    <td>
                      {Number(record.laundry_liters).toFixed(2)} L
                    </td>

                    <td>
                      {Number(record.gardening_liters).toFixed(2)} L
                    </td>

                    <td className="table-total">
                      {Number(record.total_liters).toFixed(2)} L
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        )}

      </section>

    </div>
  )
}

export default Consumption
