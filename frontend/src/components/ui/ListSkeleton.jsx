import Skeleton from './Skeleton'
import Card from './Card'

const ListSkeleton = ({ count = 3, showAvatar = false, showActions = false }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} className="p-4">
          <div className="flex items-start gap-4">
            {showAvatar && (
              <Skeleton variant="avatar" rounded />
            )}
            <div className="flex-1 space-y-2">
              <Skeleton variant="title" width="60%" />
              <Skeleton variant="text" lines={2} />
              {showActions && (
                <div className="flex gap-2 mt-3">
                  <Skeleton variant="button" width="80px" />
                  <Skeleton variant="button" width="80px" />
                </div>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

export default ListSkeleton
