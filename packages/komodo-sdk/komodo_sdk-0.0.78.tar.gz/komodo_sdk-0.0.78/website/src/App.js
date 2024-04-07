import RoutesMain from "./RouterMain";
import { Toaster } from "react-hot-toast";
import { RoleStore } from "./contexts/roleContext";
import 'react-modern-drawer/dist/index.css'
export default function App() {
  return (
    <RoleStore>
      <RoutesMain />
      <Toaster position="top-right" reverseOrder={false} />
    </RoleStore>
  )
}
