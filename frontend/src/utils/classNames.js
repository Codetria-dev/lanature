// Utility to combine CSS classes
export default function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}
