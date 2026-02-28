import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import heroImage from '../assets/hero-editorial.jpg';
import lifestyle1 from '../assets/lifestyle-1.jpg';
import lifestyle2 from '../assets/lifestyle-2.jpg';

export default function Landing() {
  return (
    <section className="min-h-screen pt-6 pb-16 px-8">
      <div className="max-w-7xl mx-auto">

        {/* Editorial headline */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-6 items-end mb-16 lg:mb-24">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="lg:col-span-7"
          >
            <p className="font-body text-[11px] tracking-[0.35em] uppercase text-primary mb-6 font-medium">
              Your Personal Stylist · Issue Nº 01
            </p>
            <h1 className="font-display text-5xl sm:text-6xl md:text-7xl lg:text-[5.5rem] leading-[0.92] font-bold text-foreground">
              Every outfit
              <br />
              tells a{' '}
              <span className="italic font-normal text-primary">story.</span>
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="lg:col-span-4 lg:col-start-9 font-body text-muted-foreground text-[15px] leading-relaxed"
          >
            We read yours — every texture, palette, and silhouette — then search
            thousands of shops to find only the pieces that belong in your wardrobe.
          </motion.p>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.9 }}
          className="mb-16 lg:mb-24"
        >
          <Link
            to="/upload"
            className="inline-block bg-foreground text-background font-body text-[11px] tracking-[0.35em] uppercase px-10 py-4 hover:bg-primary transition-colors duration-300"
          >
            Begin Your Scan
          </Link>
        </motion.div>

        {/* Asymmetric editorial image grid */}
        <div className="grid grid-cols-12 gap-4 lg:gap-5">
          {/* Main hero — large */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="col-span-12 lg:col-span-7 editorial-frame"
          >
            <div className="overflow-hidden">
              <img
                src={heroImage}
                alt="Editorial fashion — woman on a European street"
                className="w-full h-[50vh] lg:h-[70vh] object-cover"
              />
            </div>
            <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mt-3 px-1">
              The art of dressing with intention
            </p>
          </motion.div>

          {/* Side column — stacked smaller images */}
          <div className="col-span-12 lg:col-span-5 flex flex-col gap-4 lg:gap-5">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, delay: 0.8 }}
              className="editorial-frame flex-1"
            >
              <div className="overflow-hidden h-full">
                <img
                  src={lifestyle1}
                  alt="Morning light at a café"
                  className="w-full h-full min-h-[200px] object-cover"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.9, delay: 1.0 }}
              className="editorial-frame flex-1"
            >
              <div className="overflow-hidden h-full">
                <img
                  src={lifestyle2}
                  alt="Burgundy and cream — a color story"
                  className="w-full h-full min-h-[200px] object-cover"
                />
              </div>
            </motion.div>
          </div>
        </div>

        {/* Editorial pull quote */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 1 }}
          className="mt-16 lg:mt-24 max-w-3xl mx-auto text-center"
        >
          <blockquote className="font-display text-2xl md:text-3xl italic text-foreground leading-relaxed">
            "Style is a way to say who you are
            <br className="hidden md:block" />
            without having to speak."
          </blockquote>
          <p className="font-body text-[11px] tracking-[0.3em] uppercase text-muted-foreground mt-5">
            — Rachel Zoe
          </p>
        </motion.div>
      </div>
    </section>
  );
}
