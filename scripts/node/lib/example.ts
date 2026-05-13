export function exampleMessage(runtime: string): string {
  if (!runtime) {
    throw new Error('runtime is required')
  }

  return `example runtime=${runtime} status=ok`
}
