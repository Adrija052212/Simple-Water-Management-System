
import { createContext, useContext, useEffect, useState } from 'react'
import { getHouseholds } from '../services/api'

// Create a shared household context
const HouseholdContext = createContext(null)

// Provider component
export function HouseholdProvider({ children }) {
  const [household, setHousehold] = useState(null)
  const [loadingHousehold, setLoadingHousehold] = useState(true)
  const [householdError, setHouseholdError] = useState('')

  // Fetch the registered household
  async function refreshHousehold() {
    try {
      setLoadingHousehold(true)
      setHouseholdError('')

      const response = await getHouseholds()
      const households = response.households || []

      setHousehold(households.length > 0 ? households[0] : null)

    } catch (error) {
      setHousehold(null)
      setHouseholdError(
        error.message || 'Unable to retrieve household information.'
      )
    } finally {
      setLoadingHousehold(false)
    }
  }

  // Fetch household information when the application starts
  useEffect(() => {
    refreshHousehold()
  }, [])

  return (
    <HouseholdContext.Provider
      value={{
        household,
        householdId: household?.household_id || null,
        loadingHousehold,
        householdError,
        refreshHousehold,
      }}
    >
      {children}
    </HouseholdContext.Provider>
  )
}

// Custom hook for accessing household information
export function useHousehold() {
  const context = useContext(HouseholdContext)

  if (!context) {
    throw new Error(
      'useHousehold must be used inside HouseholdProvider.'
    )
  }

  return context
}
