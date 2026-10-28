export function getReadingSteps(routes, slug) {
 return routes.flatMap((route, index) => {
  const position = route.slugs.indexOf(slug);
  if (position < 0) return [];
  return [{ id: route.id || String(index + 1).padStart(2, '0'), title: route.title,
   step: position + 1, total: route.slugs.length,
   previous: route.slugs[position - 1] || null, next: route.slugs[position + 1] || null }];
 });
}
export function selectReadingRoute(steps, requestedId) {
 return steps.find(step => step.id === requestedId) || steps[0] || null;
}
