
import { useState } from 'react'
import { predictConsumption } from '../services/api'

const initialForm = {
  Household_Size: '4',
  Bathing_Events: '4',
  Kitchen_Sessions: '3',
  Laundry_Loads: '1',
  Gardening_Duration_Minutes: '20',
}

const activityConfig = [
  { name: 'Bathroom', key: 'bathroom_liters', color: 'bar-blue', icon: '🚿' },
  { name: 'Kitchen', key: 'kitchen_liters', color: 'bar-teal', icon: '🍽️' },
  { name: 'Laundry', key: 'laundry_liters', color: 'bar-purple', icon: '🧺' },
  { name: 'Gardening', key: 'gardening_liters', color: 'bar-green', icon: '🌱' },
]

function Prediction() {
  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [predictionTime, setPredictionTime] = useState(null)

  const householdSize = Number(form.Household_Size)
  const bathingEvents = Number(form.Bathing_Events)

  function handleChange(event) {
    const { name, value } = event.target

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }))

    setResult(null)
    setError('')
  }

  function validateForm() {
    const fields = [
      'Household_Size',
      'Bathing_Events',
      'Kitchen_Sessions',
      'Laundry_Loads',
      'Gardening_Duration_Minutes',
    ]

    for (const field of fields) {
      const value = form[field]

      if (value === '' || !Number.isFinite(Number(value))) {
        return `${field.replaceAll('_', ' ')} is required.`
      }

      if (Number(value) < 0) {
        return 'Activity values cannot be negative.'
      }

      if (!Number.isInteger(Number(value))) {
        return 'All activity inputs must be whole numbers.'
      }
    }

    if (householdSize < 1 || householdSize > 6) {
      return 'Household size must be between 1 and 6.'
    }

    if (bathingEvents > householdSize) {
      return 'Bathing events cannot exceed household size.'
    }

    if (Number(form.Kitchen_Sessions) < 2 ||
        Number(form.Kitchen_Sessions) > 4) {
      return 'Kitchen sessions must be between 2 and 4, matching the training data.'
    }

    if (Number(form.Laundry_Loads) > 3) {
      return 'Laundry loads cannot exceed 3, matching the training data.'
    }

    const gardening = Number(form.Gardening_Duration_Minutes)

    if (
      gardening !== 0 &&
      (gardening < 10 || gardening > 60)
    ) {
      return 'Gardening duration must be 0 or between 10 and 60 minutes.'
    }

    return null
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setResult(null)

    const validationError = validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      const payload = {
        Household_Size: Number(form.Household_Size),
        Bathing_Events: Number(form.Bathing_Events),
        Kitchen_Sessions: Number(form.Kitchen_Sessions),
        Laundry_Loads: Number(form.Laundry_Loads),
        Gardening_Duration_Minutes: Number(
          form.Gardening_Duration_Minutes
        ),
      }

      const response = await predictConsumption(payload)

      if (!response.predicted_consumption) {
        throw new Error('The prediction response is incomplete.')
      }

      setResult(response.predicted_consumption)
      setPredictionTime(new Date())
    } catch (err) {
      setError(err.message || 'Unable to generate prediction.')
    } finally {
      setLoading(false)
    }
  }

  const activities = result
    ? activityConfig.map((activity) => ({
        ...activity,
        value: Number(result[activity.key]) || 0,
      }))
    : []

  const total = Number(result?.total_liters) || 0

  return (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE / PREDICTION</p>
          <h1>Water consumption prediction</h1>
          <p className="page-description">
            Estimate household water demand using the trained KNN regression model.
          </p>
        </div>

        <span className="sample-badge">KNN REGRESSION</span>
      </div>

      <section className="panel prediction-panel">
        <div className="panel-heading">
          <div>
            <h2>Household activity details</h2>
            <p>Enter the expected daily household activities.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="prediction-form-grid">
            <div className="form-field">
              <label htmlFor="Household_Size">Household size</label>
              <input
                id="Household_Size"
                name="Household_Size"
                type="number"
                min="1"
                max="6"
                step="1"
                value={form.Household_Size}
                onChange={handleChange}
                required
              />
              <small>Allowed range: 1–6 members</small>
            </div>

            <div className="form-field">
              <label htmlFor="Bathing_Events">Bathing events</label>
              <input
                id="Bathing_Events"
                name="Bathing_Events"
                type="number"
                min="0"
                max={householdSize}
                step="1"
                value={form.Bathing_Events}
                onChange={handleChange}
                required
              />
              <small>Cannot exceed household size</small>
            </div>

            <div className="form-field">
              <label htmlFor="Kitchen_Sessions">Kitchen sessions</label>
              <input
                id="Kitchen_Sessions"
                name="Kitchen_Sessions"
                type="number"
                min="2"
                max="4"
                step="1"
                value={form.Kitchen_Sessions}
                onChange={handleChange}
                required
              />
              <small>Allowed range: 2–4 sessions</small>
            </div>

            <div className="form-field">
              <label htmlFor="Laundry_Loads">Laundry loads</label>
              <input
                id="Laundry_Loads"
                name="Laundry_Loads"
                type="number"
                min="0"
                max="3"
                step="1"
                value={form.Laundry_Loads}
                onChange={handleChange}
                required
              />
              <small>Allowed range: 0–3 loads</small>
            </div>

            <div className="form-field">
              <label htmlFor="Gardening_Duration_Minutes">
                Gardening duration (minutes)
              </label>
              <input
                id="Gardening_Duration_Minutes"
                name="Gardening_Duration_Minutes"
                type="number"
                min="0"
                max="60"
                step="1"
                value={form.Gardening_Duration_Minutes}
                onChange={handleChange}
                onBlur={(event) => {
                    const value = Number(event.target.value)

                    if (value > 0 && value < 10) {
                    setError('Gardening duration must be 0 or between 10 and 60 minutes.')
                    }
                }}
                required
              />
              <small>Enter 0 or a duration between 10–60 minutes</small>
            </div>
          </div>

          {error && (
            <div className="form-alert error-alert" role="alert">
              {error}
            </div>
          )}

          <button
            className="submit-button"
            type="submit"
            disabled={loading}
          >
            {loading
              ? 'Predicting consumption...'
              : 'Predict water consumption'}
          </button>
        </form>
      </section>

      {result && (
        <section className="panel prediction-result">
          <div className="panel-heading">
            <div>
              <h2>Prediction results</h2>
              <p>Estimated daily water demand by activity.</p>
            </div>
            <span className="panel-tag">KNN MODEL</span>
          </div>

          <div className="prediction-total">
            <div>
              <span>Total predicted demand</span>
              <small>
                {predictionTime?.toLocaleString() || ''}
              </small>
            </div>
            <strong>{total.toFixed(2)} L</strong>
          </div>

          <div className="prediction-breakdown">
            {activities.map((activity) => {
              const percentage = total > 0
                ? (activity.value / total) * 100
                : 0

              return (
                <div
                  className="prediction-activity"
                  key={activity.key}
                >
                  <div className="breakdown-info">
                    <span>
                      {activity.icon} {activity.name}
                    </span>
                    <strong>{activity.value.toFixed(2)} L</strong>
                  </div>

                  <div className="progress-track">
                    <div
                      className={`progress-fill ${activity.color}`}
                      style={{
                        width: `${Math.min(100, percentage)}%`,
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

          <div className="dashboard-note">
            These estimates are generated using a KNN model trained on
            simulated household consumption data. They demonstrate
            model-based estimation and should not be interpreted as
            validated real-world measurements.
          </div>
        </section>
      )}
    </div>
  )
}

export default Prediction
