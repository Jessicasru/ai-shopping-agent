import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Menu, X } from 'lucide-react';

export default function Nav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.nav
      initial={{ y: -10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="fixed top-0 left-0 right-0 z-50 bg-background/90 backdrop-blur-md"
    >
      <div className="max-w-7xl mx-auto px-8 py-5 flex items-center justify-between">
        <Link to="/" className="font-display text-xl tracking-[0.15em] font-semibold text-foreground uppercase">
          Stylai
        </Link>

        <div className="hidden md:flex items-center gap-10 font-body text-[13px] tracking-[0.08em] uppercase">
          <Link to="/upload" className="text-muted-foreground hover:text-foreground transition-colors duration-300">
            The Scan
          </Link>
          <Link to="/profile" className="text-muted-foreground hover:text-foreground transition-colors duration-300">
            Your Profile
          </Link>
          <Link to="/matches" className="text-muted-foreground hover:text-foreground transition-colors duration-300">
            Curated Picks
          </Link>
          <span className="w-px h-4 bg-border" />
          <Link to="/upload" className="text-primary hover:text-primary/80 transition-colors duration-300 font-medium">
            Begin
          </Link>
        </div>

        <button className="md:hidden text-foreground" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="md:hidden border-t border-border bg-background px-8 py-6 space-y-4"
        >
          <Link to="/upload" onClick={() => setIsOpen(false)} className="block text-sm text-muted-foreground tracking-wide uppercase">The Scan</Link>
          <Link to="/profile" onClick={() => setIsOpen(false)} className="block text-sm text-muted-foreground tracking-wide uppercase">Your Profile</Link>
          <Link to="/matches" onClick={() => setIsOpen(false)} className="block text-sm text-muted-foreground tracking-wide uppercase">Curated Picks</Link>
        </motion.div>
      )}
    </motion.nav>
  );
}
