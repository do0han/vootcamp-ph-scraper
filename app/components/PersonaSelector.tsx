'use client'

import { memo, useCallback } from 'react'
import { Check } from 'lucide-react'

export interface Persona {
  id: string
  name: string
  description: string
  emoji: string
  color: string
}

interface PersonaSelectorProps {
  personas: Persona[]
  selectedPersona: Persona | null
  onSelect: (persona: Persona) => void
}

function PersonaSelectorComponent({ personas, selectedPersona, onSelect }: PersonaSelectorProps) {
  const handleSelect = useCallback((persona: Persona) => {
    onSelect(persona)
  }, [onSelect])

  return (
    <div className="space-y-3">
      {personas.map((persona) => (
        <div
          key={persona.id}
          onClick={() => handleSelect(persona)}
          className={`
            relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
            ${selectedPersona?.id === persona.id
              ? 'border-ph-blue bg-blue-50 shadow-md'
              : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
            }
          `}
        >
          <div className="flex items-center space-x-4">
            <div
              className={`
                w-12 h-12 rounded-lg flex items-center justify-center text-xl
                bg-gradient-to-r ${persona.color}
              `}
            >
              {persona.emoji}
            </div>
            
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{persona.name}</h3>
              <p className="text-sm text-gray-600">{persona.description}</p>
            </div>

            {selectedPersona?.id === persona.id && (
              <div className="absolute top-3 right-3">
                <div className="w-6 h-6 bg-ph-blue rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export const PersonaSelector = memo(PersonaSelectorComponent) 