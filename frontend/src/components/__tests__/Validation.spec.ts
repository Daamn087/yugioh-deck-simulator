import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DeckBuilder from '../DeckBuilder.vue'
import { useSimulationStore } from '../../store'

describe('DeckBuilder Validation', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('clamps card category count to 0', async () => {
        const wrapper = mount(DeckBuilder, {
            props: {
                deckSize: 40,
                handSize: 5,
                contents: {}
            },
            global: {
                plugins: [createTestingPinia({
                    initialState: {
                        simulation: {
                            cardCategories: [
                                { name: 'Ash Blossom', count: 3, subcategories: [] }
                            ]
                        }
                    },
                    stubActions: false
                })]
            }
        })

        const store = useSimulationStore()

        // Card count input should be the 3rd one (after deck size and hand size)
        const countInput = wrapper.findAll('input[type="number"]')[2]
        if (countInput) {
            expect(countInput.exists()).toBe(true)

            // Set value to -5
            const input = countInput.element as HTMLInputElement
            input.value = '-5'
            await countInput.trigger('input')

            // Check if store was updated with 0 instead of -5
            expect(store.cardCategories[0].count).toBe(0)
        }
    })

    it('clamps deck size and hand size to 0', async () => {
        const wrapper = mount(DeckBuilder, {
            props: {
                deckSize: 40,
                handSize: 5,
                contents: {}
            },
            global: {
                plugins: [createTestingPinia({
                    stubActions: false
                })]
            }
        })

        const inputs = wrapper.findAll('input[type="number"]')
        const deckSizeInput = inputs[0]
        const handSizeInput = inputs[1]

        if (deckSizeInput) {
            await deckSizeInput.setValue(-10)
            expect(wrapper.emitted('update:deckSize')?.[0]).toEqual([0])
        }

        if (handSizeInput) {
            await handSizeInput.setValue(-1)
            expect(wrapper.emitted('update:handSize')?.[0]).toEqual([0])
        }
    })
})
