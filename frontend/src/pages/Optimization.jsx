
import { useEffect, useState } from 'react'
import { recommendConsumption } from '../services/api'
import { useHousehold } from '../context/HouseholdContext'

const initialForm = {
  Household_Size: 4,
  Bathing_Events: 4,
  Kitchen_Sessions: 3,
  Laundry_Loads: 1,
  Gardening_Duration_Minutes: 20,
  available_budget_liters: 350,
}

const activityColors = {
  bathroom: 'bar-blue',
  kitchen: 'bar-teal',
  laundry: 'bar-purple',
  gardening: 'bar-green',
}

function Optimization() {
  const {
    household,
    householdId,
    loadingHousehold,
    householdError,
  } = useHousehold()

  const [form, setForm] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Automatically use the registered household size
  useEffect(() => {
    if (household) {
      setForm(previous => ({
        ...previous,
        Household_Size: Number(household.household_size),
        Bathing_Events: Number(household.household_size),
      }))
    }
  }, [household])

  function handleChange(event) {
    const { name, value } = event.target

    setForm(previous => ({
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
      'available_budget_liters',
    ]

    for (const field of fields) {
      const value = form[field]

      if (value === '' || !Number.isFinite(Number(value))) {
        return `${field.replaceAll('_', ' ')} is required.`
      }

      if (Number(value) < 0) {
        return 'Input values cannot be negative.'
      }
    }

    const householdSize = Number(form.Household_Size)
    const bathingEvents = Number(form.Bathing_Events)
    const kitchenSessions = Number(form.Kitchen_Sessions)
    const laundryLoads = Number(form.Laundry_Loads)
    const gardening = Number(form.Gardening_Duration_Minutes)

    if (
      !Number.isInteger(householdSize) ||
      householdSize < 1 ||
      householdSize > 6
    ) {
      return 'Household size must be between 1 and 6.'
    }

    if (household && householdSize !== Number(household.household_size)) {
      return 'Household size must match your registered household.'
    }

    if (!Number.isInteger(bathingEvents) || bathingEvents > householdSize) {
      return 'Bathing events must be whole numbers and cannot exceed household size.'
    }

    if (
      !Number.isInteger(kitchenSessions) ||
      kitchenSessions < 2 ||
      kitchenSessions > 4
    ) {
      return 'Kitchen sessions must be between 2 and 4.'
    }

    if (
      !Number.isInteger(laundryLoads) ||
      laundryLoads > 3
    ) {
      return 'Laundry loads must be between 0 and 3.'
    }

    if (
      !Number.isInteger(gardening) ||
      (
        gardening !== 0 &&
        (gardening < 10 || gardening > 60)
      )
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
        available_budget_liters: Number(
          form.available_budget_liters
        ),
      }

      const response = await recommendConsumption(payload)
      setResult(response)

    } catch (err) {
      if (err.data?.optimization) {
        setResult(err.data)
      } else {
        setError(err.message || 'Unable to optimize water allocation.')
      }
    } finally {
      setLoading(false)
    }
  }

  const optimization = result?.optimization
  const allocations = optimization?.activity_allocations

  const conservationData = result?.conservation_recommendations
  const recommendations = conservationData?.recommendations || []

  // Wait for household information
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

      {/* PAGE HEADING */}
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE / OPTIMIZATION</p>
          <h1>Water allocation optimizer</h1>
          <p className="page-description">
            Find an optimized household water allocation within your
            available budget.
          </p>
        </div>

        <span className="sample-badge">
          KNN + LINEAR PROGRAMMING
        </span>
      </div>

      {/* INPUT FORM */}
      <section className="panel optimization-input-panel">

        <div className="panel-heading">
          <div>
            <h2>Household requirements</h2>
            <p>
              Enter daily activity details and your available water budget.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>

          <div className="optimization-form-grid">

            <div className="form-field">
              <label htmlFor="opt-household">Household size</label>
              <input
                id="opt-household"
                name="Household_Size"
                type="number"
                min="1"
                max="6"
                step="1"
                value={form.Household_Size}
                readOnly
                required
              />
              <small>
                Automatically taken from your registered household
              </small>
            </div>

            <div className="form-field">
              <label htmlFor="opt-bathing">Bathing events</label>
              <input
                id="opt-bathing"
                name="Bathing_Events"
                type="number"
                min="0"
                max={form.Household_Size}
                step="1"
                value={form.Bathing_Events}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="opt-kitchen">Kitchen sessions</label>
              <input
                id="opt-kitchen"
                name="Kitchen_Sessions"
                type="number"
                min="2"
                max="4"
                step="1"
                value={form.Kitchen_Sessions}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="opt-laundry">Laundry loads</label>
              <input
                id="opt-laundry"
                name="Laundry_Loads"
                type="number"
                min="0"
                max="3"
                step="1"
                value={form.Laundry_Loads}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="opt-gardening">
                Gardening duration (minutes)
              </label>
              <input
                id="opt-gardening"
                name="Gardening_Duration_Minutes"
                type="number"
                min="0"
                max="60"
                step="1"
                value={form.Gardening_Duration_Minutes}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field budget-field">
              <label htmlFor="opt-budget">
                Available water budget (litres)
              </label>
              <input
                id="opt-budget"
                name="available_budget_liters"
                type="number"
                min="0"
                step="0.01"
                value={form.available_budget_liters}
                onChange={handleChange}
                required
              />
            </div>

          </div>

          {error && (
            <div className="form-alert error-alert">
              {error}
            </div>
          )}

          <button
            className="submit-button"
            type="submit"
            disabled={loading}
          >
            {loading
              ? 'Optimizing allocation...'
              : 'Predict and optimize water'}
          </button>

        </form>
      </section>

      {/* RESULTS */}
      {result && optimization && (
        <>

          <section className="panel optimization-result-panel">

            <div className="panel-heading">
              <div>
                <h2>Optimization results</h2>
                <p>
                  Combined output from KNN prediction and linear programming.
                </p>
              </div>

              <span className="panel-tag">
                {optimization.success ? 'FEASIBLE' : 'INFEASIBLE'}
              </span>
            </div>

            {/* SUMMARY CARDS */}
            <div className="optimization-summary-grid">

              <div className="optimization-summary-card">
                <span>Predicted demand</span>
                <strong>
                  {optimization.total_predicted_demand_liters} L
                </strong>
              </div>

              <div className="optimization-summary-card">
                <span>Available budget</span>
                <strong>
                  {optimization.available_budget_liters} L
                </strong>
              </div>

              {optimization.success ? (
                <>
                  <div className="optimization-summary-card">
                    <span>Optimized allocation</span>
                    <strong>
                      {optimization.total_allocated_liters} L
                    </strong>
                  </div>

                  <div className="optimization-summary-card highlight-summary">
                    <span>Potential demand reduction</span>
                    <strong>
                      {optimization.potential_savings_liters} L
                    </strong>
                    <small>
                      {optimization.potential_savings_percentage}%
                    </small>
                  </div>
                </>
              ) : (
                <div className="optimization-summary-card">
                  <span>Minimum required allocation</span>
                  <strong>
                    {optimization.minimum_required_liters} L
                  </strong>
                </div>
              )}

            </div>

            {/* INFEASIBLE RESULT */}
            {!optimization.success ? (
              <div className="form-alert error-alert">
                {optimization.message}
                {' '}
                Your available budget is below the minimum allocation
                required by the current optimization constraints.
              </div>
            ) : (
              <>

                {/* ACTIVITY ALLOCATION TABLE */}
                <h3 className="allocation-title">
                  Activity-wise allocation
                </h3>

                <div className="allocation-table-wrapper">
                  <table className="records-table">
                    <thead>
                      <tr>
                        <th>Activity</th>
                        <th>Predicted</th>
                        <th>Minimum</th>
                        <th>Allocated</th>
                        <th>Reduced</th>
                      </tr>
                    </thead>

                    <tbody>
                      {Object.entries(allocations || {}).map(
                        ([activity, values]) => (
                          <tr key={activity}>
                            <td className="activity-name">
                              {activity.charAt(0).toUpperCase() +
                                activity.slice(1)}
                            </td>

                            <td>{values.predicted_liters} L</td>
                            <td>{values.minimum_liters} L</td>

                            <td className="table-total">
                              {values.optimized_liters} L
                            </td>

                            <td>{values.water_reduced_liters} L</td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>

                {/* ALLOCATION PROGRESS BARS */}
                <div className="allocation-visual">
                  {Object.entries(allocations || {}).map(
                    ([activity, values]) => {
                      const predicted = values.predicted_liters
                      const allocated = values.optimized_liters

                      const percentage = predicted > 0
                        ? (allocated / predicted) * 100
                        : 0

                      return (
                        <div className="allocation-item" key={activity}>
                          <div className="allocation-label">
                            <span>
                              {activity.charAt(0).toUpperCase() +
                                activity.slice(1)}
                            </span>

                            <strong>
                              {allocated.toFixed(2)} / {predicted.toFixed(2)} L
                            </strong>
                          </div>

                          <div className="progress-track">
                            <div
                              className={`progress-fill ${activityColors[activity]}`}
                              style={{
                                width: `${Math.min(percentage, 100)}%`,
                              }}
                            />
                          </div>
                        </div>
                      )
                    }
                  )}
                </div>

                <div className="dashboard-note">
                  Potential demand reduction is the difference between
                  predicted demand and optimized allocation. It is not a
                  measurement of physically saved water.
                </div>

              </>
            )}

          </section>

          {/* CONSERVATION RECOMMENDATIONS */}
          {optimization.success && (
            <section className="panel conservation-panel">

              <div className="panel-heading">
                <div>
                  <p className="eyebrow">PERSONALIZED CONSERVATION PLAN</p>
                  <h2>Recommended water-saving actions</h2>
                  <p>
                    Practical suggestions based on the activities where
                    the optimizer identified reduction targets.
                  </p>
                </div>

                <span className="panel-tag">
                  {recommendations.length} ACTIVITIES
                </span>
              </div>

              {recommendations.length > 0 ? (
                <div className="recommendation-list">

                  {recommendations.map(item => (
                    <article
                      className="recommendation-card"
                      key={item.activity}
                    >

                      <div className="recommendation-card-header">

                        <div>
                          <h3>{item.title}</h3>
                          <span className="recommendation-activity">
                            {item.activity}
                          </span>
                        </div>

                        <span
                          className={`priority-badge priority-${item.priority.toLowerCase()}`}
                        >
                          {item.priority} priority
                        </span>

                      </div>

                      <div className="recommendation-metrics">

                        <div>
                          <span>Predicted usage</span>
                          <strong>{item.predicted_liters} L</strong>
                        </div>

                        <div>
                          <span>Optimized allocation</span>
                          <strong>{item.optimized_liters} L</strong>
                        </div>

                        <div>
                          <span>Reduction target</span>
                          <strong>
                            {item.target_reduction_liters} L
                          </strong>
                        </div>

                        <div>
                          <span>Target reduction</span>
                          <strong>
                            {item.target_reduction_percentage}%
                          </strong>
                        </div>

                      </div>

                      <h4>Suggested actions</h4>

                      <ul className="recommendation-actions">
                        {item.actions.map((action, index) => (
                          <li key={index}>{action}</li>
                        ))}
                      </ul>

                    </article>
                  ))}

                </div>
              ) : (
                <div className="dashboard-note">
                  No activity-wise reduction targets were identified
                  for this allocation. The household is already within
                  its available water budget under the current model.
                </div>
              )}

              {conservationData?.disclaimer && (
                <div className="dashboard-note">
                  {conservationData.disclaimer}
                </div>
              )}

            </section>
          )}

        </>
      )}

    </div>
  )
}

export default Optimization
